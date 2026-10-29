---
title: 'Default IBackgroundTaskSettings.is_feature_enabled to False'
type: 'chore'
created: '2026-10-29'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `IBackgroundTaskSettings.is_feature_enabled` defaults to `True`, so background task queueing is on for any fresh install.

**Approach:** Change the schema default in `opengever/bgtasks/interfaces.py` to `False`.

</frozen-after-approval>

## Implementation Notes

- Changed `default=True` to `default=False` in `opengever/bgtasks/interfaces.py`.
- Sites that already ran the registry upgrade keep their stored value (`True`); only new installs and fresh registrations get `False`. No upgrade step added, as none was requested.
- Test setup already disables the feature explicitly (`opengever/core/testing.py`, `IntegrationTestCase.setUp`), so no test changes were needed.
- Review layers skipped: one-line default change, subagents not authorized.
