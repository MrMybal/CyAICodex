"""Shared launch paths and Windows instance coordination."""
import ctypes
import os
from pathlib import Path
import subprocess
import sys
import time

import httpx


def root_path():
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent


def default_data():
    root = root_path()
    if (root / 'installed.txt').is_file():
        return Path(os.environ['LOCALAPPDATA']) / 'CyAICodex' / 'data'
    return root / 'data'


def command(*args):
    prefix = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, str(root_path() / 'run.py')]
    return prefix + list(args)


def launch_background(args):
    env = {**os.environ, 'PYINSTALLER_RESET_ENVIRONMENT': '1'}
    env.pop('CYAICODEX_MCP_TOKEN', None)
    return subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)


def launch_independent(args, visible=False):
    """Ask the user's desktop to launch, outside a client's process lifetime."""
    if os.name != 'nt':
        return launch_background(args)
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    try:
        desktop = win32com.client.Dispatch('Shell.Application').Windows().FindWindowSW(0, 0, 8, 0, 1)
        desktop.Document.Application.ShellExecute(args[0], subprocess.list2cmdline(args[1:]),
                                                  str(Path(args[0]).parent), 'open', 1 if visible else 0)
    except Exception:
        raise OSError('Le bureau Windows ne peut pas lancer CyAICodex. Ouvrez l’application depuis son raccourci.') from None
    finally:
        pythoncom.CoUninitialize()


def kernel():
    dll = ctypes.WinDLL('kernel32', use_last_error=True)
    from ctypes import wintypes as w
    for name, args, result in [
        ('CreateMutexW', [ctypes.c_void_p, w.BOOL, w.LPCWSTR], w.HANDLE),
        ('OpenMutexW', [w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        ('CreateEventW', [ctypes.c_void_p, w.BOOL, w.BOOL, w.LPCWSTR], w.HANDLE),
        ('OpenEventW', [w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        ('SetEvent', [w.HANDLE], w.BOOL), ('CloseHandle', [w.HANDLE], w.BOOL),
        ('WaitForSingleObject', [w.HANDLE, w.DWORD], w.DWORD),
    ]:
        fn = getattr(dll, name); fn.argtypes = args; fn.restype = result
    return dll


def maintenance_active():
    if os.name != 'nt':
        return False
    dll = kernel()
    handle = dll.OpenMutexW(0x100000, False, 'Local\\CyAICodex-Install')
    if handle:
        dll.CloseHandle(handle)
    return bool(handle)


class Instance:
    def __init__(self, port):
        self.dll = kernel()
        self.mutex = self.dll.CreateMutexW(None, False, f'Local\\CyAICodex-Server-{port}')
        self.owner = ctypes.get_last_error() != 183
        if not self.mutex:
            raise OSError('Cannot create CyAICodex instance lock')
        self.event = self.dll.CreateEventW(None, True, False, f'Local\\CyAICodex-Stop-{port}') if self.owner else None

    def stopped(self):
        return self.event and self.dll.WaitForSingleObject(self.event, 0) == 0

    def close(self):
        for handle in (self.event, self.mutex):
            if handle:
                self.dll.CloseHandle(handle)


def stop_server(port):
    if os.name != 'nt':
        return
    dll = kernel()
    event = dll.OpenEventW(2, False, f'Local\\CyAICodex-Stop-{port}')
    if not event:
        return
    try:
        dll.SetEvent(event)
    finally:
        dll.CloseHandle(event)
    for _ in range(200):
        handle = dll.OpenMutexW(0x100000, False, f'Local\\CyAICodex-Server-{port}')
        if not handle:
            return
        dll.CloseHandle(handle)
        time.sleep(.1)
    raise RuntimeError('CyAICodex is still stopping. Try again shortly.')


def ensure_server(port, data_dir):
    if maintenance_active():
        raise RuntimeError('CyAICodex is being updated. Reconnect after installation.')
    url = f'http://127.0.0.1:{port}/health'
    def ready():
        try:
            response = httpx.get(url, timeout=.5, trust_env=False)
        except httpx.ConnectError:
            return False
        except httpx.TimeoutException:
            return False
        if response.status_code != 200 or response.json().get('app') != 'methodes':
            raise RuntimeError('The local port is used by another application.')
        return True
    if ready():
        return
    launch_independent(command('--no-open', '--port', str(port), '--data-dir', str(data_dir)))
    deadline = time.monotonic() + 35
    while time.monotonic() < deadline:
        if maintenance_active():
            raise RuntimeError('CyAICodex is being updated.')
        if ready():
            return
        time.sleep(.2)
    raise RuntimeError('CyAICodex did not start in time.')


def watch_bridge(port):
    """Release the executable during setup even while stdin is idle."""
    if os.name != 'nt':
        return
    dll = kernel()
    while True:
        event = dll.OpenEventW(0x100000, False, f'Local\\CyAICodex-Stop-{port}')
        if event:
            try:
                if dll.WaitForSingleObject(event, 0) == 0:
                    os._exit(0)
            finally:
                dll.CloseHandle(event)
        if maintenance_active():
            os._exit(0)
        time.sleep(.2)
