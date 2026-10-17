import sys
if '--finish-install' in sys.argv:
    from skills.installation import main
elif '--mcp-stdio' in sys.argv:
    from skills.bridge import main
else:
    from skills.desktop import main

if __name__ == "__main__":
    try:
        main()
    except Exception:
        import logging
        import os
        logging.exception("Impossible de démarrer CyAICodex")
        if os.name == "nt" and not any(flag in sys.argv for flag in ('--mcp-stdio', '--finish-install', '--stop')):
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,
                "CyAICodex n'a pas pu démarrer. Consultez data\\cyaicodex.log et vérifiez que le port 8765 est libre.",
                "CyAICodex", 16)
        raise
