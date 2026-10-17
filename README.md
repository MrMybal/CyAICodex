# CyAICodex

English · [Français](README.fr.md)

Maintained by **Cyberalien**.

A local Windows library of reusable methods and image references, shared with AI clients through MCP. The application runs in the Windows notification area and provides a browser interface.

## Install

Download **CyAICodex-Setup-0.6.3.exe** from the [GitHub releases](https://github.com/MrMybal/CyAICodex/releases), run the installer, and open CyAICodex from the Start menu or desktop shortcut. Python is not required.

**English is the default language.** French is available through **FR / EN** or **Settings > App language**. Existing saved language preferences are preserved. Language selection also applies to the tray menu and the language requested from the assistant; personal methods, projects and images are not automatically translated.

The installer offers a desktop shortcut and startup with Windows. Closing the browser tab leaves the server running; use the tray menu to reopen or quit it. Installed library data is stored separately in `%LOCALAPPDATA%\CyAICodex\data`. Uninstalling preserves the library.

The application and MCP transport use the same `CyAICodex.exe`. Keep its `_internal` directory alongside it: components are installed once instead of being extracted into Temp at each launch.

## Methods and image references

- Markdown methods with titles, summaries, categories, tags and revision history.
- Global, project-type and project-specific scopes, with draft, published and archived states.
- Accent-insensitive full-text search, prefix matching, weighted ranking and pagination.
- Optimistic version checks to prevent concurrent edits from overwriting each other.
- PNG, JPEG and WebP image references with detailed descriptions, preservation instructions, permitted uses and original files.
- A bundled GitHub publication checklist, added once in the library's initial language. User edits to the example are preserved.

Only published resources within a connection's scope are available through MCP. Library JSON exports cover methods and classification; to back up images and revision history too, stop the application and copy the entire data directory. Encrypted credentials remain tied to their Windows account.

## Connect AI clients

Use **Connections** to create a named connection with its project scope and write permissions. Copy the generated token when it is shown; revoking the connection invalidates it.

**Configure and test** supports Codex, Claude Desktop and OpenCode. These clients launch `CyAICodex.exe --mcp-stdio`, which starts the shared server when needed. Reconnect the MCP server or restart the client after changing its configuration.

Streamable HTTP is also available at `http://127.0.0.1:8765/mcp`, using `Authorization: Bearer <token>`. Multiple clients can connect simultaneously. Remote cloud clients cannot reach this PC's localhost directly.

Available tools:

- Methods: `get_context`, `search_methods`, `get_method`, `create_method`, `update_method`.
- Images: `search_images`, `get_image`, `view_image`, `import_image`, `update_image`.

Suggested client instruction:

> At the start of a task, consult CyAICodex: call get_context, then search_methods and get_method for applicable practices. Respect the connection's scope. Save reusable practices when I ask you to.

MCP provides access to the library; it cannot force an agent to consult it. Configure that behavior in each client's instructions. Each token has its own scope, so clients can use different project contexts simultaneously.

## Integrated assistant

Supported integrations include Codex, Claude Code, OpenCode, Ollama, OpenAI API, Claude API, Antigravity, Command Code, CodeBuddy, OpenRouter and LM Studio. Availability depends on installed clients, account access and the selected model. Desktop and CLI authentication can be separate; consumer subscriptions and API credentials are distinct.

Local credentials are encrypted with Windows DPAPI. Reading, searching and manually editing the library does not require an AI call. Assistant requests send the conversation and selected references to the chosen provider. Image support depends on the adapter and model.

Additional connector settings provide availability checks, model discovery and response tests. A response test can consume the provider's quota. Models are not installed automatically. See the [detailed French documentation](README.fr.md) for connector-specific behavior, limits and configuration paths.

## Updates

**Settings > Updates** checks for stable GitHub releases at startup and every six hours; automatic checks can be disabled. Downloading and installing is a separate action. The application checks the installer size and GitHub SHA-256 digest before opening it. MCP clients may need reconnecting after an update.

For private repositories, use the local Git GitHub credentials or a repository token with **Contents: read**. Public repositories work without authentication.

To migrate a portable installation, quit it and run the installer with `/LEGACYDATA="absolute path to data"`. The original library is preserved, and an existing destination library is never replaced.

## Build and test

Install Python 3.11 or newer, then run `Installer.ps1` in PowerShell. Dependencies are pinned in `requirements.lock.txt`.

```powershell
.\Construire-Exe.ps1
.\Construire-Installateur.ps1 -Iscc "path to ISCC.exe"
.\.venv\Scripts\python.exe -m pytest -q
node tests/i18n_browser.cjs
```

The application is built in `dist/CyAICodex/`; the installer is written to `dist/`. Inno Setup 6 is required to build the installer. Use the installer to update installed copies.

UI translations are stored in `methodes/web/translations.tsv`. French source strings and English translations are kept together; interpolated user content is preserved. Unrecognized messages from external providers remain in their original language.

A release uses a `vMAJOR.MINOR.PATCH` tag and a `CyAICodex-Setup-MAJOR.MINOR.PATCH.exe` asset with a GitHub SHA-256 digest. Drafts, prereleases and older versions are not offered as updates.
