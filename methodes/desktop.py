import argparse
import asyncio
import logging
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

import httpx
import uvicorn

from .server import create_app
from .store import Store
from .i18n import language, translate
from .startup import startup_enabled, set_startup
from . import __version__

ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent


def toggle_startup(icon=None, item=None, port=8765, data_dir=None):
    set_startup(not startup_enabled(), port, data_dir)


def make_image():
    from PIL import Image, ImageDraw
    with Image.open(Path(__file__).parent / "web" / "logo-cy-book.png") as source:
        image = source.convert("RGBA")
    # Clip the app badge, just as border-radius does in the web interface.
    # Preserve the white monogram inside the circular badge.
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).ellipse((3, 3, image.width - 4, image.height - 4), fill=255)
    image.putalpha(mask)
    return image.resize((256, 256), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description="CyAICodex — bibliothèque de méthodes et serveur MCP local")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--headless", action="store_true", help="Serveur seul, sans icône de notification")
    parser.add_argument("--no-open", action="store_true", help="Ne pas ouvrir l'interface au démarrage")
    parser.add_argument("--enable-startup", action="store_true", help="Activer le démarrage avec Windows pour cette installation")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Le port doit être compris entre 1024 et 65535.")
    args.data_dir.mkdir(parents=True, exist_ok=True)
    if args.enable_startup:
        set_startup(True, args.port, args.data_dir)
    from logging.handlers import RotatingFileHandler
    logging.basicConfig(level=logging.INFO, handlers=[RotatingFileHandler(args.data_dir / "methodes.log",
                        maxBytes=2_000_000, backupCount=2, encoding="utf-8")],
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("CyAICodex %s — %s", __version__, "exécutable Windows" if getattr(sys, "frozen", False) else "Python")
    store = Store(args.data_dir)
    url = f"http://127.0.0.1:{args.port}"
    def open_app(icon=None, item=None):
        webbrowser.open(url + "/#token=" + store.setting("admin_token"))

    # A second launch opens the existing instance instead of starting another tray/server.
    try:
        r = httpx.get(url+"/health", timeout=1, trust_env=False)
        if r.status_code == 200 and r.json().get("app") == "methodes":
            if not args.no_open:
                open_app()
            return
    except (httpx.HTTPError, ValueError):
        pass
    app = create_app(args.data_dir, args.port)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=args.port, log_config=None, access_log=False))
    if args.headless:
        # asyncio.run retains the Windows Proactor loop needed for Codex subprocesses.
        asyncio.run(server.serve())
        return
    import pystray
    thread = threading.Thread(target=lambda: asyncio.run(server.serve()), name="methodes-mcp", daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        if not thread.is_alive():
            raise RuntimeError("Le serveur n'a pas pu démarrer. Vérifiez le port et le journal.")
        time.sleep(.05)
    if not server.started:
        raise RuntimeError("Le serveur n'a pas démarré dans le délai prévu.")
    def quit_app(icon, item):
        server.should_exit = True
        icon.stop()

    icon = pystray.Icon("CyAICodex", make_image(), "CyAICodex · serveur MCP actif",
        menu=pystray.Menu(pystray.MenuItem(lambda item: translate("Ouvrir CyAICodex", language(store)), open_app, default=True),
                         pystray.MenuItem(lambda item: translate("Démarrer avec Windows", language(store)), lambda icon, item: toggle_startup(icon, item, args.port, args.data_dir), checked=lambda item: startup_enabled()),
                         pystray.Menu.SEPARATOR,
                         pystray.MenuItem(lambda item: translate("Quitter et arrêter le serveur", language(store)), quit_app)))
    def language_changed():
        icon.title = "CyAICodex · " + translate("Serveur MCP actif", language(store))
        icon.update_menu()
    app.state.language_changed = language_changed
    language_changed()
    def setup(icon):
        icon.visible = True
        app.state.tray_active = True
        logging.info("Icône de notification Windows active")
        if not args.no_open:
            open_app()
    try:
        icon.run(setup=setup)
    finally:
        server.should_exit = True
        thread.join(timeout=10)


if __name__ == "__main__":
    main()
