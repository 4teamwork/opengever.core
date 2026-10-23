---
title: 'Lock Objects During Queued Move'
type: 'feature'
created: '2026-07-14'
status: 'done'
baseline_commit: '61147818e7a342e3f6e234201ff79998ab34405c'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Objects queued for a background move (via `MoveItemsForm.handle_submit` or `opengever.api.move.Move.reply`) stay fully editable while their `move-objects` task is pending, so a user can modify or re-move content whose location is about to change out from under them.

**Approach:** Add a new `MOVE_LOCK` lock type in `opengever.locking.lock`; lock each cut object with it right before its `move-objects` task is queued, and have `MoveObjectsTask.execute()` clear the lock(s) by UID once the task finishes, regardless of outcome.

## Boundaries & Constraints

**Always:**
- New lock type in `opengever/locking/lock.py`: `LOCK_TYPE_MOVE_LOCK = u'object.move.lock'` / `MOVE_LOCK = LockType(LOCK_TYPE_MOVE_LOCK, stealable=True, user_unlockable=True, timeout=MAX_TIMEOUT)` — same style as the existing custom lock types in that module.
- Only the code paths that actually call `queue_task(TASK_TYPE, ...)` apply the lock — not the synchronous `paste_clipboard()` fallback branches (`move_instantly` in `MoveItemForm`, and `admin_unit is None` in both call sites). Those have no pending window to protect.
- `opengever/dossier/move_items.py` `MoveItemsForm.handle_submit`: after `manage_cutObjects`, in the `else` branch that queues the task, call `ILockable(obj).lock(MOVE_LOCK)` before `queue_task(...)`, and add `u'object_uids': [obj.UID()]` to its arguments.
- `opengever/api/move.py` `Move.reply`: a single clipboard/task can bundle multiple source ids sharing one parent. Track the actual objects (not just their ids) per parent so that, in the `queue_task` branch, every object in that group is locked (`ILockable(obj).lock(MOVE_LOCK)`) and all their UIDs go into a new `object_uids` task argument.
- `opengever/bgtasks/move.py` `MoveObjectsTask.execute()`: read `object_uids` from task arguments. Wrap the existing body so that, in a `finally`, every UID is resolved via `portal_catalog.unrestrictedSearchResults(UID=...)` (unrestricted, same pattern as the existing `destination_uid` lookup) and unlocked with `ILockable(obj).unlock(MOVE_LOCK)` if still locked. This must run on every exit path — missing/invalid arguments, unresolved destination, unresolved user, expected paste failure, or successful paste — so a failed or skipped move never leaves a permanent lock.

**Ask First:**
- Confirm `ILockable(obj).unlock(MOVE_LOCK)` has no permission gate that would require the worker to hold the original queuing user's security context (`run_as_user`) to succeed — existing precedent (`linked_workspaces.py`) calls `unlock()` unconditionally without one, but if it turns out to fail under the worker's default context, stop and confirm before wrapping the unlock in `run_as_user`.

**Never:**
- Don't lock/unlock in the synchronous fallback (`paste_clipboard()` called inline) paths.
- Don't add lock-info UI (`opengever/locking/info.py` custom template mapping, new `.pt` templates) for `MOVE_LOCK` — out of scope; it falls back to the existing default lock-info template.
- Don't change `IMovabilityChecker`/`DocumentMovabiliyChecker` — its existing generic `ILockable(...).locked()` check already blocks re-moving a document that's locked for any reason, including this new lock.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Queued single move | `MoveItemsForm` submits one doc, admin unit present | Object locked with `MOVE_LOCK` before `queue_task`; unlocked once `execute()` finishes | N/A |
| Queued multi-source API move | `POST @move` with 2 source docs sharing one parent | Both objects locked before the single `queue_task` call; both unlocked after `execute()` | N/A |
| Instant/inline move | `move_instantly=True` or `admin_unit is None` | No `MOVE_LOCK` ever applied | N/A |
| Task can't resolve destination/user | `destination_uid` missing/not found, or `user_id` unresolved | Task returns early, nothing pasted | `object_uids` still unlocked in `finally` |
| Paste raises expected exception | `ValueError`/`CopyError`/`ResourceLockedError`/`Unauthorized` from `paste_clipboard` | Warning logged, no raise | `object_uids` still unlocked in `finally` |

</frozen-after-approval>

## Code Map

- `opengever/locking/lock.py` -- add `LOCK_TYPE_MOVE_LOCK` / `MOVE_LOCK`
- `opengever/dossier/move_items.py` -- `MoveItemsForm.handle_submit`, lock before `queue_task`
- `opengever/api/move.py` -- `Move.reply`, track objects (not just ids) per parent, lock + pass `object_uids` before `queue_task`
- `opengever/bgtasks/move.py` -- `MoveObjectsTask.execute`, unlock `object_uids` in a `finally`
- `opengever/bgtasks/tests/test_move.py` -- existing coverage to extend
- `opengever/api/tests/test_move.py` -- existing coverage to extend
- `opengever/dossier/tests/test_move_items.py` -- `MoveItemsHelper` fixtures used by both test suites

## Tasks & Acceptance

**Execution:**
- [x] `opengever/locking/lock.py` -- add `LOCK_TYPE_MOVE_LOCK` / `MOVE_LOCK` -- new lock type for in-flight moves
- [x] `opengever/dossier/move_items.py` -- lock `obj` before `queue_task` in `handle_submit`, add `object_uids` arg -- protects queued single-object moves
- [x] `opengever/api/move.py` -- track objects per parent instead of ids; lock all + pass `object_uids` before `queue_task` -- protects queued multi-object moves
- [x] `opengever/bgtasks/move.py` -- read `object_uids`, unlock them in a `finally` wrapping `execute()`'s body -- guarantees the lock is always cleared
- [x] `opengever/bgtasks/tests/test_move.py` -- add tests for lock-on-enqueue and unlock-on-execute (success, expected-failure, and early-return paths)
- [x] `opengever/api/tests/test_move.py` -- add a test that a multi-source queued move locks and unlocks all objects

**Acceptance Criteria:**
- Given a document is cut and queued via `MoveItemsForm`, when `handle_submit` runs, then the document is locked with `MOVE_LOCK` immediately and stays locked until its background task executes.
- Given a `MoveObjectsTask` finishes — successfully, with an expected paste failure, or via early-return due to missing destination/user — when `execute()` returns, then every object in `object_uids` is no longer locked with `MOVE_LOCK`.
- Given `move_instantly` is `True` or no admin unit is configured, when a move happens, then `MOVE_LOCK` is never applied.
- Given a document locked for a pending move, when a user tries to move it again before the task completes, then the existing `ILockable(...).locked()` check in `DocumentMovabiliyChecker` already rejects it — no new check needed.

## Design Notes

`opengever/api/move.py` currently groups source items by parent into `parents_ids: {parent: [id, ...]}`, only ever keeping ids because that's all `self.clipboard(parent, ids)` needs. Since locking needs live objects (for `ILockable(...)` and `.UID()`), rename this to `parents_objs: {parent: [obj, ...]}` and derive `ids = [obj.getId() for obj in objs]` right before the `self.clipboard(parent, ids)` call — everything downstream is otherwise unchanged.

## Verification

**Commands:**
- `bin/test -m opengever.bgtasks -t test_move` -- expect all pass, including new lock/unlock tests
- `bin/test -m opengever.api -t test_move` -- expect all pass
- `bin/test -m opengever.dossier -t test_move_items` -- expect all pass

## Suggested Review Order

**New lock type**

- Entry point — the new `MOVE_LOCK`, styled after the existing custom lock types in this module.
  [`lock.py:30`](../../opengever/locking/lock.py#L30)

**Lock-before-queue at both call sites**

- Single-object queue path: lock right before `queue_task`, UID passed through for later cleanup.
  [`move_items.py:211`](../../opengever/dossier/move_items.py#L211)

- Multi-object queue path: objects (not ids) tracked per parent so every object in the group gets locked.
  [`move.py:76`](../../opengever/api/move.py#L76)

- Lock + pass all UIDs for the group in the `queue_task` branch specifically.
  [`move.py:114`](../../opengever/api/move.py#L114)

**Guaranteed unlock on task completion**

- `object_uids` read up front so it's available to the `finally` regardless of which branch exits.
  [`bgtasks/move.py:33`](../../opengever/bgtasks/move.py#L33)

- Existing body wrapped in `try/finally` — unlock runs on every exit path (missing args, unresolved destination/user, expected paste failure, success).
  [`bgtasks/move.py:91`](../../opengever/bgtasks/move.py#L91)

- Unlock resolved unrestricted by UID, guarded by `.locked(MOVE_LOCK)`, with a warning if the UID can't be found in the catalog.
  [`bgtasks/move.py:104`](../../opengever/bgtasks/move.py#L104)

**Tests**

- Lock-on-enqueue coverage for both call sites, plus the instant/inline paths asserting no lock is ever applied.
  [`bgtasks/test_move.py:91`](../../opengever/bgtasks/tests/test_move.py#L91)

- Unlock-on-execute coverage across success, expected failure, and every early-return path.
  [`bgtasks/test_move.py:255`](../../opengever/bgtasks/tests/test_move.py#L255)

- Multi-parent case: one request spanning two parents must queue two tasks, each locking only its own object.
  [`api/test_move.py:372`](../../opengever/api/tests/test_move.py#L372)
