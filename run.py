import sys
if '--mcp-stdio' in sys.argv:
    from methodes.bridge import main
else:
    from methodes.desktop import main

if __name__ == "__main__":
    try:
        main()
    except Exception:
        import logging
        import os
        logging.exception("Impossible de démarrer CyAICodex")
        if os.name == "nt" and '--mcp-stdio' not in sys.argv:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,
                "CyAICodex n'a pas pu démarrer. Consultez data\\methodes.log et vérifiez que le port 8765 est libre.",
                "CyAICodex", 16)
        raise
