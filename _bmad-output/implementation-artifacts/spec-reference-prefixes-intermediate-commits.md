---
title: 'Intermediate commits and resume in UpdateReferencePrefixesTask'
type: 'feature'
created: '2026-10-30'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `UpdateReferencePrefixesTask` reindexes all children of a repository folder in a single transaction. If the worker is restarted midway, all progress is lost and the whole subtree is reindexed again.

**Approach:** Commit a checkpoint every 100 reindexed objects via `commit_checkpoint`, storing the last processed path. On a re-run, the task reads the checkpoint and continues with the objects not yet processed.

</frozen-after-approval>

## Implementation Notes
Changed `opengever/repository/tasks.py`: `reindex_children_with_new_prefix` now processes brains sorted by path, skips paths <= `last_path`, and calls `commit_checkpoint({'last_path': ...})` every `CHECKPOINT_INTERVAL` (100) objects. The task passes the stored checkpoint in. The subscriber's direct call is unchanged (both new args optional). Added two tests; the Python 2.7 test environment is unavailable locally, so they were not run. Review subagents were skipped (not requested); self-review only.

## Spec Change Log

## Review Triage Log

- medium (fixed): repo uses towncrier; added `changes/backgroundtasks-reference-prefixes-checkpoints.feature`.
- low (rejected): sorting materialises brains (not objects) and `getPath()` is cheap metadata; ZODB cache GC already runs on each commit, so no explicit `cacheMinimize` is needed.
- false: resume test does prove skipping; if nothing were skipped, the second run would equal `first_run`, not `first_run[1:]`.
- low (rejected): fixture-size assumption, extra edge-case tests, str/unicode comparison (Plone ids are ASCII), docstring on base class.
- false/pre-existing: a broken object failing deterministically on retry is the same as before; spec files are tracked in the repo like earlier ones.
