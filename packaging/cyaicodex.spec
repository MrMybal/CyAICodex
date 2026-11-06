# Build with: .venv/Scripts/python.exe -m PyInstaller packaging/cyaicodex.spec
from pathlib import Path
import shutil
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

root = Path(SPECPATH).parent
web_assets = [
    "index.html", "style.css", "app.js", "images.css", "images.js", "settings.js",
    "help.js", "connectors.js", "updates.js", "mcp-setup.css", "mcp-setup.js", "i18n.js", "translations.tsv",
    "logo-cy-book.png", "logo-cy-book-transparent.png", "logo-cy-book-transparent.ico",
]
assets = [(str(root / "skills" / "web" / name), "skills/web") for name in web_assets]
assets += [(str(root / "skills" / "examples" / name), "skills/examples")
           for name in ("github-privacy.fr.json", "github-privacy.en.json")]
help_root = root / "Documentation"
if not (help_root / "Documentation.html").is_file() or not (help_root / "DocData" / "manifest.json").is_file():
    raise SystemExit("Build documentation first: npm ci --prefix .CyDocBuild; npm --prefix .CyDocBuild run build")
assets += collect_data_files("mcp") + collect_data_files("jsonschema_specifications")
assets += copy_metadata("mcp", recursive=True)

analysis = Analysis(
    [str(root / "run.py")],
    pathex=[str(root)],
    binaries=[],
    datas=assets,
    hiddenimports=["pystray._win32"] + collect_submodules("uvicorn"),
    hookspath=[],
    runtime_hooks=[],
    excludes=["pytest", "tkinter"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz, analysis.scripts, [],
    exclude_binaries=True,
    name="CyAICodex",
    debug=False,
    strip=False,
    upx=False,
    console=True,
    hide_console='hide-early',
    icon=str(root / "skills" / "web" / "logo-cy-book-transparent.ico"),
    version=str(root / "packaging" / "version.txt"),
)

collection = COLLECT(exe, analysis.binaries, analysis.datas, strip=False, upx=False, name="CyAICodex")

# The public reader is installed once, beside the executable. Build sources stay private.
help_destination = Path(DISTPATH).resolve() / "CyAICodex" / "Documentation"
if not help_destination.is_relative_to(root.resolve() / "dist"):
    raise SystemExit("Documentation destination must stay inside the application dist directory")
shutil.copytree(help_root, help_destination, dirs_exist_ok=True)
