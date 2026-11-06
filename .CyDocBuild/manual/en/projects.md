---
id: projects
title: Projects, types and visibility
description: Control visibility with global, project-type and project scopes.
section: Library
order: 5
revision: 2
parent: skills
---


## Choose who can see each resource {#content}


1. In Projects & types, create a type such as Web application, then a project linked to it.
2. Assign each Skill/image to Global, that type or that specific project.
3. In Connections, choose each AI’s project or type context and whether global resources are included.

## A project connection can read {#diagram-1}

```diagram
{"type": "flow", "title": "A project connection can read", "nodes": [{"id": "context", "label": "Project connection", "x": 0, "y": 120, "width": 220}, {"id": "global", "label": "Globals when included", "x": 340, "y": 0, "width": 300}, {"id": "type", "label": "Project-type skills", "x": 340, "y": 120, "width": 300}, {"id": "project", "label": "This project’s skills", "x": 340, "y": 240, "width": 300}], "edges": [{"from": "context", "to": "global"}, {"from": "context", "to": "type"}, {"from": "context", "to": "project"}]}
```

- **Global skills** — Only when Include global is enabled.
- **Project-type skills** — Resources for this project’s type.
- **Project skills** — Resources for this specific project.

A project connection combines that project, its type and optionally globals. A type-only connection sees that type and optionally globals. Without project/type, only globals can be visible when included. Other projects stay outside scope.

```callout
{"type": "tip", "title": "Remember", "body": "Each connection has its own context. Multiple clients can work on different projects simultaneously. Write access covers every accessible resource, including globals when included."}
```

## Screenshot {#illustration}

```image
{"id": "projects-illustration", "src": "assets/images/project-scopes.jpg", "alt": "A sample project associated with a project type.", "title": "A sample project associated with a project type.", "controls": "minimal"}
```
