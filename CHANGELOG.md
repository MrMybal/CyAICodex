# Changelog

[Français](CHANGELOG.fr.md) · [README](README.md) · [Release 0.9.1](https://github.com/MrMybal/CyAICodex/releases/tag/v0.9.1)

## Current version and status

**CyAICodex 0.9.1 · Beta · Windows x64.** Available for testing and feedback before stable availability.

### Documented limitations

- Only a Windows x64 installer is published. The installer and executable are not Authenticode-signed.
- The server is local to an awake PC. There is no cloud sync or multi-device library service; a remote cloud client cannot reach this PC's localhost directly.
- Search is lexical, without embeddings or semantic similarity.
- Image references are still PNG, JPEG or WebP; CyAICodex stores originals and instructions but does not generate images. Vision support depends on provider and model.
- The integrated assistant does not provide a resumable native provider session or token-by-token output. Save useful work as Skills or documents.
- JSON export covers Skills and classification, not a full backup, and there is no general JSON import button. Full backups must include the entire stopped data folder.

### Bug reports

These release notes do not publish a separate bug-by-bug list. Use the [issue tracker](https://github.com/MrMybal/CyAICodex/issues) for current reports and the [troubleshooting guide](https://mrmybal.github.io/CyAICodex/Documentation.html#/en/troubleshooting) for diagnosis. Include the version and redacted reproduction steps when reporting a problem.

## 0.9.1

- Update the bundled CyDoc reader with header search, Ctrl+K, hierarchical navigation, title descriptions, themes and reading-position restoration.
- Provide complete English and French user guides and public MCP/Python help references, with localized screenshots and diagrams.
- Keep assistant guidance separate in DocAI.md and exclude documentation build files from the installed manual.
- Install Documentation/Documentation.html beside the executable and preserve existing chapter links and help entry points.

## 0.9.0

- Migrate the full English/French documentation to the bundled CyDoc file reader.
- Open offline help from Documentation, contextual help, F1, the tray or --open-help, without a documentation web server.
- Keep chapter IDs and compatible legacy links; add image zoom and in-window enlargement.
- Generate and validate documentation in the application build, with explicit translation revisions.


## 0.8.0

- Add a complete offline Documentation section in English and French, with English as the default.
- Twenty searchable chapters cover Skills, images, projects, MCP setup, providers, permissions, backups, updates and troubleshooting.
- Bundle English/French screenshots and accessible diagrams; open the manual separately or print the selected chapter.
- Include the AGPL v3 license in the installer and installed application.


## 0.7.1

- Provide client-specific setup guidance through the read-only get_setup_guide MCP tool.
- Download an English or French Markdown guide from Connections to share with an AI before connecting it.
- Publish guide discovery links in /mcp-info, with verification and troubleshooting steps.


## 0.7.0

- Rename the library's methods to Skills, with English source folders and script filenames.
- Provide the GitHub privacy starter skill in both English and French. Preserve existing adaptations and add only the missing language.
- Add search_skills, get_skill, create_skill and update_skill MCP tools, retaining the previous names for existing clients.
- Consolidate version notes in this changelog. English remains the default interface language; French is available.

## 0.6.3

- Default to English while preserving saved language preferences.
- Add an English repository overview and separate French documentation.

## 0.6.2

- Install shared application components once instead of extracting them into Temp at each launch.

## 0.6.1

- Add a GitHub publication checklist example.

## 0.6.0

- Add the Windows installer, integrated MCP transport and GitHub release updates.

## 0.5.0

- Add Antigravity, Command Code, CodeBuddy, OpenRouter and LM Studio connectors.
- Include the existing local library, project scopes, image references, assistant, Windows tray and bilingual interface.

Older release notes remain available in Git history.
