---
title: '@backgroundtasks task type filter'
type: 'feature'
created: '2026-10-29'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The `@backgroundtasks` endpoint can only filter by status and admin unit, so an admin cannot narrow the list to one kind of task.

**Approach:** Add an optional `filters.task_type` (multiple values allowed, like `status`) that restricts results to tasks with one of the given `task_type` values. No default; without it all types are returned. Values are not validated (task types are registered dynamically), so unknown types simply yield no results.

</frozen-after-approval>

## Implementation Notes

- Added `filters.task_type` in `opengever/api/backgroundtasks.py`, a test (`create_task` gained a `task_type` argument), and `changes/backgroundtasks-api-task-type.feature`.
- Tests could not be run (no buildout in checkout).
- Blind Hunter review skipped: subagents not explicitly authorized; change is a single `in_` filter.
