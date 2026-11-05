---
id: building-help
title: Build and maintain documentation
description: Sources, builds, local integration and translation contracts.
section: Integration
order: 240
revision: 1
---

## Build and maintain the manual {#content}

The Windows application is Python (FastAPI, SQLite and pystray), with a browser interface. Documentation is a separate, bundled CyDoc reader. It opens from a local file URL and does not need the application server, Python, Node.js, an AI account or Internet to read. Source development can also use it on platforms with Python and a browser; the distributed executable and installer target Windows x64.

## Regenerate and distribute {#build}

Install Node.js 22 or newer for generation, plus the application's Python build environment. From the repository root:

```powershell
npm ci
npm run docs:build
npm run docs:check
.\.venv\Scripts\python.exe -m pytest -q
node tests/help_browser.cjs
node tests/i18n_browser.cjs
.\Build-App.ps1
.\Build-Installer.ps1 -Iscc "path to ISCC.exe"
```

Both docs commands regenerate the export and validate links, media, aliases and translations. They clean only build/help and build/cydoc-input. They do not delete authored sources. Build-App and Build-Installer install locked Node dependencies, generate documentation, and package the complete build/help tree in _internal/help. PyInstaller uses an onedir distribution; the reader is not extracted into a new temporary folder on each opening. Use the installer for installed application updates.

The standalone output is build/help/index.html. Copy the entire build/help directory when distributing it separately: data.js, viewer scripts and styles, selected module scripts, assets, manifests, translation report and license notice. Do not copy only index.html.

## Content and scope {#sources}

Author user guides in docs/content/en and docs/content/fr. Screenshots and the unchanged logo are in docs/assets. The builder also includes the repository README in each language, the license, release notes, and annotated Python help integration. The README becomes the Application reference page. README headings are rendered as bold labels there to avoid deriving public anchors from translated headings; its stable entry anchor is content.

The explicit source extraction allowlist contains only skills/documentation.py, using CyDoc's public extractComments API and its Python triple-quoted @doc annotations. No personal database, logs, credentials, environment files, ignored checkout or whole-drive index is imported. The existing MCP tools reference and setup guides remain accurate runtime-generated descriptions; setup-guide downloads are still MCP connection features and are not removed by the documentation migration. No Doxygen, TypeDoc, semantic C++ indexing or automatic API generation is claimed for this Python application.

## Stable addresses {#addresses}

Keep page IDs, heading anchors and media IDs identical in both languages. Localized text can change independently. Examples of cross-page links:

```markdown
[Restore a backup](doc:backup#restore)
[Skill screenshot](doc:skills?media=skills-illustration)
```

Existing twenty chapter IDs remain unchanged. Aliases overview → welcome, quickstart → quick-start and api-links → tools are declared in cydoc.config.json. Add an alias before renaming a published page. The route is index.html#/en/backup/restore or index.html#/en/skills?media=skills-illustration; media state belongs after the hash.

The Python host uses Path.as_uri() before adding the encoded route. It validates page, anchor and media against the export. See [Python help integration](doc:help-integration#contracts).

## Open help from the application {#entry-points}

Documentation in the navigation and Windows tray opens the welcome chapter. The ? button and F1 target the current screen: Skills, Images, Projects, Assistant, MCP connections or Providers/settings. In skill and image dialogs F1 targets their respective chapters. A control can specify data-help-page, data-help-section and data-help-media for a precise destination.

```powershell
CyAICodex.exe --open-help --help-language fr --help-page backup --help-section restore
CyAICodex.exe --open-help --help-page skills --help-media skills-illustration
CyAICodex.exe --open-help --help-page quick-start --print-help-url
```

The final command prints the validated URL without opening a browser or starting a server. In source mode, replace CyAICodex.exe with .\.venv\Scripts\python.exe run.py. The authenticated POST /api/help/open is a native launcher, not a reader server. Anonymous sites cannot invoke it. Old /help?lang=fr#backup links retain their chapter through the launcher when the application is running and the browser session is authenticated; otherwise use the tray or executable. The retired JSON /help/content endpoint returns HTTP 410 with guidance.

## Languages and translation tracking {#translations}

English is the content default and French is fully provided. New help openings pass the application's saved language; the reader's own selector changes its view without changing that application preference. CyDoc falls back to English for missing translated content and indicates the fallback. Release builds require both languages for every page, matching heading IDs, and no missing, outdated or untracked translations.

Increase the English frontmatter revision when meaning changes. Update the French sourceRevision only after reviewing and updating the translation. Track generated pages in docs/generated-revisions.json with revision and sourceRevision.fr; annotations themselves do not support these revision tags in CyDoc 0.1.0. Maintain the translated changelog alongside the English release notes. Never mark an untranslated change current just to pass the check. The generated Translation report page and translation-report.json report status.

## Modules and local assets {#modules}

Only image is enabled: screenshots benefit from zoom, pan and in-window enlargement. Image controls use the minimal presentation and remain accessible on focus or touch devices. Flow diagrams compile to accessible static SVG and retain text descriptions; they do not need graph. There are no videos, GIF frame controls, 3D meshes or media collections in this application's existing manual, so video, gif, mesh, gallery and graph are excluded. Three.js is neither installed nor shipped.

Use CyDoc JSON rich fences with asset paths starting assets/. Never add remote scripts, CDN fonts, external image URLs or runtime JSON fetches. The stock CyDoc exporter supplies classic scripts and local resource/module providers. The application-owned docs/reader.html sets branding and English initial markup; assets/host.js clarifies the application's AGPL license and CyDoc's MIT license without modifying CyDoc bundles.

## Appearance, accessibility and reading state {#experience}

The CyDoc light and dark themes use green accents consistent with the app. Its theme selector, keyboard navigation, local search, table of contents, print control, in-window media enlargement and touch controls remain available. Escape exits enlargement; image zoom and annotations stay inside the reader window. Screenshots have descriptive alternatives and diagrams include their full textual explanations.

Reading positions, bookmarks and notes use CyDoc's stable CyAICodex storage namespace. Browser policies for file origins may prevent persistence; the viewer still reads the manual and allows exporting personal reader data. Old reader positions were not imported: the old manual did not persist per-chapter positions. Changing the installation path or browser can change file-origin storage. Verify storage and keyboard/touch behavior in the browser used for distribution.

## Verification and known limits {#verification}

Run docs:check, the Python suite and both Node DOM harnesses after editing. Checks cover bilingual IDs and anchors, local resource existence, permitted module bundles, contextual launch requests, authentication and URL encoding. Test the packaged --print-help-url command to check the installed resource path independently of the server.

On the target Windows browser, open the file directly while offline, then check an internal link, an anchor, language switching, search, screenshot enlargement/Escape, keyboard focus, reading position restoration and each help entry point. Automated DOM fixtures and a successful export do not establish native browser behavior. Other operating systems and touch devices require their own tests. No codecs or WebGL are required because no video or mesh module is enabled.
