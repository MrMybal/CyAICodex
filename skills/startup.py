"""Shared Windows login startup setting for the tray and the local UI."""
import os
import subprocess
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "Methode"
ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent


def startup_enabled():
    if os.name != "nt":
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, VALUE_NAME)
        return bool(value)
    except FileNotFoundError:
        return False


def startup_command(port=8765, data_dir=None):
    if getattr(sys, "frozen", False):
        args = [sys.executable]
    else:
        args = [str(Path(sys.executable).with_name("pythonw.exe")), str(ROOT / "run.py")]
    args.extend(["--no-open", "--port", str(port), "--data-dir", str(Path(data_dir or ROOT / "data").resolve())])
    return subprocess.list2cmdline(args)


def set_startup(enabled, port=8765, data_dir=None):
    if os.name != "nt":
        raise ValueError("Le démarrage automatique est disponible sous Windows uniquement.")
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, startup_command(port, data_dir))
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass
    return startup_enabled()
