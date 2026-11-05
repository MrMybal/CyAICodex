---
id: updates
title: Updates, migration and uninstall
description: Automatic checks, when enabled, run shortly after startup and every six hours. They do not install automatically. Drafts, prereleases, older versions and assets without a valid expected digest are not installed.
section: User guide
order: 15
revision: 1
---

## Updates, migration and uninstall {#content}


1. Open Settings > Updates and Check for updates.
2. For a private repository, enable local Git GitHub credentials or supply a repository token with Contents: read access. Public releases need no authentication.
3. If a newer stable version is offered, Download and install. The installer’s size and GitHub SHA-256 digest are checked before the wizard opens.
4. Complete the installer and its license screen. The server/connections stop temporarily. Reopen the app and reconnect clients afterwards.

Automatic checks, when enabled, run shortly after startup and every six hours. They do not install automatically. Drafts, prereleases, older versions and assets without a valid expected digest are not installed.

## Portable migration {#portable-migration}

Quit the portable app, then run the installer with /LEGACYDATA="absolute path to data". It copies a consistent library and preserves the original. An existing destination library is not replaced. Recognized MCP entries are updated while other servers are kept; use Configure and test for manual repairs.

The normal install location is %LOCALAPPDATA%\Programs\CyAICodex. Uninstall through Windows Apps or the installed uninstaller. The library in %LOCALAPPDATA%\CyAICodex\data is preserved. Uninstalling does not revoke external accounts or remove every AI client configuration.
