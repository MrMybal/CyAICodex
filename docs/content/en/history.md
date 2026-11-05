---
id: history
title: History and concurrent edits
description: Each saved edit records a revision. If another client changed the record since you opened it, saving returns a conflict instead of overwriting that edit. Reload the latest version, compare your changes, then save deliberately.
section: User guide
order: 4
revision: 1
---

## History and concurrent edits {#content}


1. Open an existing Skill and expand Version history.
2. Choose Resume this version to load an earlier snapshot. Review the fields before saving.
3. Save to create a new current version. Loading an old snapshot does not erase later history.

Each saved edit records a revision. If another client changed the record since you opened it, saving returns a conflict instead of overwriting that edit. Reload the latest version, compare your changes, then save deliberately.

MCP writers send expected_version from get_skill or get_image. A conflict requires reading again. Image-description history does not restore older image pixels; import visual variants as separate resources.
