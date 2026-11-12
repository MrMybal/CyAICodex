# Documentation build workspace

This directory contains authoring sources and build tools, never installed with the reader.

From the application root, with Node.js 22+ and Python 3.11+:

```powershell
npm ci --prefix .CyDocBuild
npm --prefix .CyDocBuild run build
npm --prefix .CyDocBuild run check
```

Both commands regenerate `Documentation/`; `check` is not read-only. `Build-App.ps1` runs the same build before packaging, and the PyInstaller spec copies the complete reader next to the executable. `Build-Installer.ps1` includes that folder. No Node/Python toolchain is required for the installed manual.

- `manual/en` is the original; `manual/fr` is the complete translation. Preserve page IDs, explicit heading/media IDs and parents. Increment English `revision` for prose changes and update French `sourceRevision` only after translating.
- `assets` contains reviewed public screenshots, the app logo and license text. Images use the image module; diagrams compile to SVG. No mesh, Three.js, graph, gallery, video or GIF dependency is needed.
- `api-prose.json` owns bilingual MCP descriptions. `export-api.py` reads only public tool declarations from `skills/server.py` with Python AST, emitting neutral records for the public `cydoc/api-import` adapter. It does not import the server or distribute implementations. Add any new parameter description in both languages.
- Explicit `@doc` comments in `skills/documentation.py` use the public `cydoc/extract` adapter. No recursive source scan or SourceFile pages are enabled.
- `reader.html` is an application HTML shell with English metadata and the app icon. Viewer bundles are unmodified. `index-redirect.html` preserves former root URLs and their query/fragment for GitHub Pages.
- `DocAI.md` combines CyDoc’s generated guidance and the app’s public bilingual setup guide; it is outside the human reader and search index.
- `vendor/provenance.json` pins the upstream Git revision, archive hash and MIT notice. CyDoc currently retains version 0.1.0 across revisions; do not infer freshness from the version alone.
- `.generated` is disposable build input. `internal` holds private work notes and previous integration references; neither is published or installed.

The build validates links and translation revisions; it also checks matching translated anchors. Review actual language quality and inspect browser layout separately. Browser file-origin storage policies can affect bookmarks and reading-position persistence.

The documentation build also packages `integrations/skills/cyaicodex` with the standard-library helper `tools/package_agent_skill.py`. The ZIP, raw SKILL.md and checksums are sidecar downloads in `Documentation/AgentSkills/`, outside the human navigation/search. Application builds copy these with the complete manual; existing released installers are not retroactively modified.
