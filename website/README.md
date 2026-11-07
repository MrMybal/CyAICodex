# CyAICodex showcase

Maintained English/French presentation for CyAICodex 0.9.1 Beta. The generated static folder includes the application's real, complete CyDoc manual. English is the default; `?lang=fr` selects French. Assets and manual links are relative and work under a static project subpath.

From the repository root, with Node.js 22+, the existing locked CyDoc dependencies and Python 3.11+:

```powershell
npm ci --prefix .CyDocBuild
node website/build.mjs
node website/check.mjs
node website/preview.mjs --port=8892
```

Open [the loopback preview](http://127.0.0.1:8892/preview/cyaicodex/) or its [French edition](http://127.0.0.1:8892/preview/cyaicodex/?lang=fr) while the preview process is running. The prefix deliberately exercises hosting below a directory. Stop it with Ctrl+C. To rebuild only the showcase after an unchanged manual has already been generated, use `node website/build.mjs --skip-manual`.

The output is `dist/website/index.html`, with revisioned `assets/`, `LICENSE.txt`, `NOTICES.txt` and the entire reader in `manual/`. Copy the whole folder to another location and open `index.html` directly, or serve it with any static host. No runtime installation, web server, CDN, remote fonts or online account is required to read the showcase and its manual. GitHub source and download buttons are optional outgoing actions that require Internet. No installer is bundled in this folder.

`build.mjs` first runs the application's existing documentation build, checks version/translation consistency and copies its export intact. Showcase sources do not modify the CyDoc viewer. Build dependencies and authoring files are not copied. Changed images, scripts and styles get content-hashed URLs; HTML must be revalidated when hosted so it can reference new revisions. The preview uses `Cache-Control: no-cache`. No deployment workflow or repository settings are changed by this build.

## Editing

- `content.mjs`: complete English/French copy and verified optional destinations. Update version, status and download together when releasing.
- `template.mjs`: semantic, prerendered English page with stable section anchors and genuine manual destinations.
- `main.js`: classic local script for language selection, mobile navigation, chapter state and the in-page image dialog. No content fetches or module imports at runtime.
- `styles.css`: graphite/green presentation and responsive layouts, focus styles and reduced-motion behavior.
- `assets/`: selected public product captures and the existing CY book logo. Capture inventories and QA evidence stay in ignored working directories.

The eight views have English/French captures: library, Skill editor, images, image editor, projects/types, MCP connections, assistant preparation and the actual CyDoc welcome page. Captures use sample content; interface language does not translate user-authored resource descriptions. The assistant image shows an unsent prompt, not a generated response. The MCP capture shows setup before configuring the isolated instance, not a claim that every client is connected.

The project license remains [AGPL-3.0-only](../LICENSE), copyright 2026 Cyberalien. CyDoc keeps its MIT license and notices in the copied manual. The showcase uses CyAICodex’s own branding and screenshots.
