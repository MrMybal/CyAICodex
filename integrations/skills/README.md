# CyAICodex Agent Skill

[Français](README.fr.md) · [SKILL.md](cyaicodex/SKILL.md)

One portable `cyaicodex/SKILL.md` for Codex, Claude Code and compatible Agent Skills hosts. It teaches the agent to consult the shared library, read applicable practices, respect project scope and manage references without saving anything unless requested. Instructions are in English; the agent answers in the user's language. No provider-specific frontmatter, account details or MCP credentials are embedded.

## Install in Codex and Claude Code

From a source checkout, use PowerShell 7:

```powershell
pwsh -File .\integrations\skills\Install-Skill.ps1 -Client all
```

For manual installation, copy the complete `cyaicodex` folder into one of the locations below. This also works when script execution is restricted; no execution-policy change is required.

Choose `-Client codex` or `-Client claude-code` for just one client. Preview with `-WhatIf`. Existing identical files are left alone; differing files require `-Update`, which keeps one `.previous` backup of each replaced packaged file and preserves other files. No administrator rights are needed for your user profile.

| Client | User installation | Project installation |
| --- | --- | --- |
| Codex | `~/.agents/skills/cyaicodex/` | `.agents/skills/cyaicodex/` |
| Claude Code | `~/.claude/skills/cyaicodex/` | `.claude/skills/cyaicodex/` |

Use `-Scope Project -RootPath "path to your project"` for a project installation. `-RootPath` with the default user scope selects a different profile root. If an older/custom Codex installation loads `~/.codex/skills` instead, copy the same `cyaicodex` folder there manually; avoid installing duplicate copies into multiple paths loaded by the same client. Other hosts can use their documented Agent Skills folder.

The Skill is available after the client refreshes skills (next turn or a new session, depending on client/version). Invoke `$cyaicodex` in Codex or `/cyaicodex` in Claude Code, for example: “Find the applicable release checklist in CyAICodex.” Automatic selection is enabled by the standard metadata, but does not guarantee consultation on every turn. Add a standing client instruction if you require it at the start of every task.

## Claude app / claude.ai

Download [CyAICodex-Skill.zip](https://mrmybal.github.io/CyAICodex/AgentSkills/CyAICodex-Skill.zip), then upload and enable it under **Customize > Skills**, where your plan/workspace supports custom Skills. The ZIP contains exactly one `cyaicodex/` folder with `SKILL.md` and its license. You can also [read the standalone SKILL.md](https://mrmybal.github.io/CyAICodex/AgentSkills/SKILL.md). No script execution is needed to import the ZIP.

The desktop/code/cloud environments do not all share the same local files or tools. Uploading a Skill does not make the local MCP server reachable from a cloud session.

## Connect MCP separately

Start CyAICodex. For Codex or Claude Desktop, use **Connections > Configure and test**, choose context and permissions, then reconnect the MCP server in the client. Claude Code uses the generated configuration in its MCP settings. Ask the agent to call `get_context`, then `search_skills` and `get_skill` for a relevant result. Do not paste tokens into chat.

The Skill installs instructions only. It does not install CyAICodex, configure a server, change permissions or copy your library into the client. A cloud session cannot directly reach your PC's localhost. See the [real setup manual](https://mrmybal.github.io/CyAICodex/Documentation.html#/en/mcp).

## Build the download

```powershell
python tools/package_agent_skill.py
```

This writes `dist/agent-skills/CyAICodex-Skill.zip`, `SKILL.md` and `SHA256SUMS.txt`, without Git, network or third-party Python dependencies. The documentation build includes the same files in `Documentation/AgentSkills/`; the app's next build will ship them with its manual. `node website/build-pages.mjs` publishes them under `AgentSkills/`. Sources remain here; generated archives stay outside Git. The current application installer does not acquire a new Skill automatically.

Format references: [Codex Skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code Skills](https://code.claude.com/docs/en/skills), [Claude ZIP import](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills). The package retains CyAICodex's AGPL-3.0-only license.
