---
title: 'Move Objects Background Task'
type: 'feature'
created: '2026-07-07'
status: 'done'
baseline_commit: '3a6014c91d3aa445d023bada97cf760fc60e5080'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `manage_pasteObjects` in both `opengever.api.move.Move.reply()` and `opengever.dossier.move_items.MoveItemsForm.handle_submit()` performs the costly recursive copy/move of an object tree synchronously in-request, blocking on large dossier structures — the same class of problem already solved for reindexing via `opengever.bgtasks`.

**Approach:** Extract the paste step into a new shared `opengever.bgtasks` task type (`move-objects`) taking a `destination_uid`, the `manage_cutObjects()` clipboard string, and the queuing user's `user_id` as arguments. Both call sites keep cutting synchronously and enqueue the paste via `queue_task()`, following the enqueue/fallback pattern established by `UpdateReferencePrefixesTask`. The background worker process runs entirely as the unrestricted `system` user (`opengever/core/debughelpers.py`), but `manage_pasteObjects` enforces a destination-side Add-permission check (`_verifyObjectPaste`) against whatever security manager is active — so the task must explicitly assume the *queuing user's* real security context before pasting, via a new `run_as_user()` helper, so that check evaluates against the real acting user instead of always succeeding as `system`.

## Boundaries & Constraints

**Always:**
- Python 2.7 compatible.
- Only `manage_pasteObjects` is deferred. `manage_cutObjects()`, `IMovabilityChecker.validate_movement()`, and all other pre-flight validation (permissions, `DestinationValidator`) stay synchronous and unchanged.
- New task lives in `opengever/bgtasks/move.py` (generic infra, not owned by either calling package — mirrors `reindex_object_security.py`). Exposes `TASK_TYPE = u'move-objects'`, `paste_clipboard(destination, clipboard)` (thin wrapper around `destination.manage_pasteObjects(cb_copy_data=clipboard)`, raises normally), and `MoveObjectsTask(BaseBackgroundTask)`.
- `opengever/base/security.py` gains `run_as_user(user)` — a context manager sibling to the existing `elevated_privileges()`, taking an already-resolved `AccessControl` user object, switching to it via `newSecurityManager(getRequest(), user)`, and restoring the previous security manager in a `finally`. Unlike `elevated_privileges()`, it does not grant extra roles — it makes the *given* user's real roles/permissions the ones in effect.
- Enqueue pattern at both call sites: capture `user_id = api.user.get_current().getId()`. `get_current_admin_unit()` is `None` → call `paste_clipboard()` inline (OGDS not ready) — runs under the real request's own security manager already, no `run_as_user` needed. Otherwise `queue_task(TASK_TYPE, admin_unit.unit_id, arguments={u'destination_uid': ..., u'clipboard': ..., u'user_id': user_id})`.
- Task resolves the destination via `portal_catalog.unrestrictedSearchResults(UID=...)` + `_unrestrictedGetObject()`, mirroring `UpdateReferencePrefixesTask` — missing/unretrievable destination logs a `WARNING` and returns (task succeeds). This lookup itself stays unrestricted as today; only the `paste_clipboard()` call needs the real user's security context.
- `MoveObjectsTask.execute()` resolves the member via `api.user.get(userid=user_id)` before pasting. If `user_id` is missing or doesn't resolve to a member, log a `WARNING` and return without pasting — never fall through to pasting as the worker's default `system` user, since that would defeat the point of this mechanism.
- Inside the `run_as_user(member.getUser())` block, catch `(ValueError, CopyError, ResourceLockedError)` from `paste_clipboard()` and log a `WARNING` instead of raising — expected, non-retryable paste-time outcomes (checked-out document, no Add permission at destination, id conflict). Any other exception propagates to the worker's existing retry/failure handling unchanged.
- `opengever.api.move.Move.reply()`: after queuing, respond with HTTP 202 and the same body shape as today (list of `{source, target}`), where `target` is the *predicted* URL (`self.context.absolute_url() + '/' + id`, using the pre-cut id).
- `opengever.dossier.move_items.MoveItemsForm`: keep `manage_cutObjects()` and its `ResourceLockedError` handling inline per item; only `destination.manage_pasteObjects(clipboard)` is replaced by the enqueue/fallback. In the `admin_unit is None` fallback branch specifically, keep wrapping `paste_clipboard()` in `except (ValueError, CopyError): failed_objects.append(obj.title); continue` — this preserves today's exact synchronous behavior for that narrow path (queued-path failures are, by contrast, only logged server-side — see message wording below). Replace the "N items were moved successfully" message with "N item(s) queued to be moved". Do **not** touch `MoveItemForm.create_statusmessages` (the single-item subclass) — it keeps its current "${item} was moved." wording; out of scope for this change.

**Ask First:**
- `self.clipboard(parent, ids)` in `plone.restapi`'s `Move`/`CopyMoveBase` base class is assumed to be a thin wrapper returning `parent.manage_cutObjects(ids)` — unverified in this environment (no installed `plone.restapi` to inspect). If it does more than that, stop and confirm before proceeding.
- `MemberData.getUser()` (used to unwrap a `plone.api.user.get()` result into the raw `AccessControl` user object `run_as_user()`/`newSecurityManager()` expects) is standard Plone/CMFCore API but has no existing usage precedent in this codebase to copy from — verify this actually returns a usable user object during implementation; if it doesn't, stop and ask before improvising an alternative resolution path.
- If any `manage_pasteObjects`/`manage_cutObjects` call site beyond these two surfaces during implementation, ask before extending scope.

**Never:**
- Don't touch `opengever/inbox/forwarding.py`, `opengever/task/yearfolderstorer.py`, `opengever/task/browser/accept/utils.py`, or `opengever/base/browser/paste.py` — out of scope.
- Don't change `IMovabilityChecker` validation logic or `DestinationValidator`.
- Don't make the worker's `system` security context apply `run_as_user()` universally to other existing task types (`ReindexObjectSecurityTask`, `UpdateReferencePrefixesTask`, `ReindexDossierTitleTask`) — they intentionally rely on running as `system`/`elevated_privileges()` for operations that aren't gated by the triggering user's own permissions. `run_as_user()` is a new, opt-in primitive; only `MoveObjectsTask` uses it here.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| API move, admin unit present | POST `@move` with valid source(s) | 202; body has one `{source, target}` per item (predicted target); one `move-objects` task queued per source-parent group, with `user_id` of the requester | — |
| Form move, admin unit present | Submit `MoveItemsForm` with N valid items | N `move-objects` tasks queued (one per item); status message "N item(s) queued to be moved" | — |
| No admin unit | `get_current_admin_unit()` is `None` | Paste runs synchronously inline under the real request's security manager, exactly as today, including existing `(ValueError, CopyError)` handling in `move_items.py` | — |
| bgtasks disabled (tests) | `is_background_tasks_enabled()` is `False` | `queue_task` executes `MoveObjectsTask.execute()` synchronously in-request (which itself resolves and runs as the queuing user); existing move/move_items test suites keep passing unmodified except the noted status-code/message changes | — |
| Destination deleted before task runs | UID no longer in catalog at execution | Log `WARNING`, task succeeds, no paste performed | — |
| Queuing user no longer resolvable | `user_id` missing from arguments, or `api.user.get(userid=...)` returns `None` (deleted/deactivated account) | Log `WARNING`, task succeeds, no paste performed — never pastes as `system` | — |
| Queuing user lacks Add permission at destination | `paste_clipboard()` under `run_as_user(member)` raises `CopyError`/`Unauthorized` from `_verifyObjectPaste` | Caught (`CopyError` at least; see Ask First on `Unauthorized`), logged as `WARNING`, task succeeds, no retry, no Sentry report | — |
| Other paste-time failure (checked-out doc, lock, id conflict) | `manage_pasteObjects` raises `CopyError`/`ResourceLockedError`/`ValueError` | Logged as `WARNING`, task marked succeeded, no retry, no Sentry report; object stays in its source location | — |
| Unexpected exception during paste | e.g. `ConflictError` | Worker's existing retry/failure handling applies (retry up to `max_retries`, then `failed` + Sentry) | — |

</frozen-after-approval>

## Code Map

- `opengever/base/security.py` -- MODIFY: add `run_as_user(user)` context manager (sibling to `elevated_privileges`)
- `opengever/bgtasks/move.py` -- NEW: `TASK_TYPE`, `paste_clipboard(destination, clipboard)`, `MoveObjectsTask(BaseBackgroundTask)` (resolves queuing user, wraps paste in `run_as_user`), `register_task_type(...)`
- `opengever/api/move.py` -- MODIFY: `Move.reply()` — group by parent as today, build clipboard, capture `user_id`, enqueue (or paste inline as fallback), respond 202 with predicted target paths
- `opengever/dossier/move_items.py` -- MODIFY: `MoveItemsForm.handle_submit()` — replace inline paste with enqueue/fallback (fallback keeps its exception handling); `create_statusmessages` wording; `MoveItemForm` untouched
- `opengever/bgtasks/tests/test_move.py` -- NEW: `IntegrationTestCase` for `MoveObjectsTask`, including a test proving `paste_clipboard()` actually executes under the queuing user's security manager (not `system`)
- `opengever/api/tests/test_move.py` -- MODIFY: `assert_can_move` expects 202
- `opengever/dossier/tests/test_move_items.py` -- unchanged (bgtasks disabled by default in fixture keeps `queue_task` synchronous; `MoveItemForm` wording untouched keeps `TestMoveItem` passing)

## Tasks & Acceptance

**Execution:**
- [x] `opengever/base/security.py` -- modify -- add `run_as_user(user)` context manager using `getSecurityManager()`/`newSecurityManager(getRequest(), user)`/`setSecurityManager()`, mirroring `elevated_privileges()`'s save/restore structure
- [x] `opengever/bgtasks/move.py` -- create -- task type, `paste_clipboard`, `MoveObjectsTask` resolving `user_id` via `api.user.get()`, running `paste_clipboard()` inside `run_as_user(member.getUser())`, with expected-failure warning handling, following `UpdateReferencePrefixesTask`'s catalog-lookup structure otherwise
- [x] `opengever/api/move.py` -- modify `Move.reply()` -- import `queue_task`, `get_current_admin_unit`, `TASK_TYPE`/`paste_clipboard` from `opengever.bgtasks.move`, `api` from `plone`; capture `user_id`; enqueue per parent group instead of direct `manage_pasteObjects`; return 202 with predicted target paths
- [x] `opengever/dossier/move_items.py` -- modify `MoveItemsForm.handle_submit()` -- same imports plus `api` from `plone`; capture `user_id`; enqueue instead of direct `manage_pasteObjects`; keep `(ValueError, CopyError)` handling around the `admin_unit is None` fallback's `paste_clipboard()` call; update `create_statusmessages` wording to "queued to be moved"; leave `MoveItemForm` untouched
- [x] `opengever/bgtasks/tests/test_move.py` -- create -- test: enqueues expected task(s) with `user_id` present (API: per parent group, form: per item); test: falls back to synchronous paste when admin unit is `None`; test: `MoveObjectsTask.execute` delegates to `paste_clipboard`; test: missing destination UID is a no-op; test: missing/unresolvable `user_id` is a no-op (no paste attempted); test: `paste_clipboard()` executes with the queuing user's security manager active (spy on `getSecurityManager().getUser().getId()`); test: `CopyError`/`ResourceLockedError`/`ValueError` from `paste_clipboard` are caught and logged, not raised
- [x] `opengever/api/tests/test_move.py` -- modify `assert_can_move` -- expect 202 instead of 200

**Acceptance Criteria:**
- Given a valid `@move` request with an admin unit configured, when the request completes, then the response status is 202, the body lists `{source, target}` pairs with predicted targets, and a `move-objects` task is queued carrying the requesting user's id.
- Given `MoveItemsForm` submitted with valid items and an admin unit configured, when `handle_submit` runs, then one `move-objects` task is queued per item and the status message reads "N item(s) queued to be moved".
- Given `get_current_admin_unit()` returns `None`, when either entry point pastes, then the paste executes synchronously exactly as it does today, including existing exception handling in `move_items.py`.
- Given the existing `opengever/api/tests/test_move.py` and `opengever/dossier/tests/test_move_items.py` suites (bgtasks disabled in the fixture), when run with only the status-code and `MoveItemsForm`-message changes applied, then all tests still pass.
- Given a queued `move-objects` task whose paste raises `CopyError`, `ResourceLockedError`, or `ValueError` (including a permission failure because the queuing user lacks Add rights at the destination), when the task executes, then it completes as `succeeded` without retry and without a Sentry report, and `paste_clipboard()` is proven to have executed under that user's own security context, not `system`.

## Spec Change Log

- **2026-07-07** — Multi-agent review (blind hunter, edge-case hunter, acceptance auditor) surfaced an `intent_gap`: the original spec deferred `manage_pasteObjects` to the background worker without accounting for the worker running entirely as the unrestricted `system` user, silently bypassing `manage_pasteObjects`'s built-in destination Add-permission check (`_verifyObjectPaste`) — most severely in `move_items.py`, which had no other synchronous destination-permission guard. Human resolved by choosing to make the task assume the queuing user's real security context rather than accept the risk or add a coarser standalone permission check. **Amended:** added `run_as_user()` to `opengever/base/security.py`; both call sites now capture and pass `user_id`; `MoveObjectsTask` resolves and runs as that user, failing closed (no paste, not "paste as system") if the user can't be resolved. Also folded in two lower-severity findings from the same review round: (1) the `admin_unit is None` fallback in `move_items.py` had lost its original `(ValueError, CopyError)` handling around the paste call — restored; (2) the first implementation attempt had also changed `MoveItemForm.create_statusmessages`'s wording, which was out of spec scope and broke existing `TestMoveItem` tests — reverted to keep `MoveItemForm` untouched. **KEEP:** the core design (shared `opengever/bgtasks/move.py` task, per-call-site grouping preserved, predicted-target 202 response, expected-failure swallowing in the task) worked well and is unchanged.
- **2026-07-07** — Second review round (same three reviewers, run after implementing the `run_as_user` fix) confirmed the security fix itself works correctly (verified by a real test proving the security manager switches identity and restores afterward) and surfaced only `patch`-level gaps, all fixed in place without a further loopback: (1) the `admin_unit is None` fallback in `move_items.py` still didn't catch `ResourceLockedError` around the fallback paste call, unlike the original code's single try/except covering both cut and paste — restored; (2) the status message wording said "element(s)" instead of the spec's literal "item(s)" — corrected; (3) `MoveObjectsTask` didn't catch `AccessControl.Unauthorized`, which `_verifyObjectPaste` can now genuinely raise (a newly-reachable path specifically because paste finally runs as a real, potentially-restricted user instead of always `system`) — added to the caught-and-logged exception tuple; (4) `member.getUser()` returning `None` wasn't guarded, and the resolved real user wasn't explicitly acquisition-wrapped to `acl_users` the way `elevated_privileges()`'s synthetic user is — both addressed defensively.

## Design Notes

**Cut stays sync, paste goes async:** `manage_cutObjects()` is cheap and is where today's `ResourceLockedError` (WebDAV lock) and `IMovabilityChecker` failures already surface — those keep working exactly as before. Only the expensive recursive `manage_pasteObjects()` moves to the background, which also means the object visibly stays in its *original* location until the worker processes the task.

**`run_as_user` vs `elevated_privileges`:** `elevated_privileges()` already in this codebase grants a synthetic `Manager` role — the opposite of what's needed here, since that would *also* always pass `_verifyObjectPaste`'s check regardless of the real user's actual rights. `run_as_user()` instead switches to the real, already-existing member object, so the destination's actual local/global roles for that user are what gets evaluated.

**Predicted target, not actual:** The 202 response's `target` is computed from the pre-cut id, not the real paste result. In the rare case of an id collision at the destination, `manage_pasteObjects` would rename the object during the deferred paste and the predicted URL would be stale — accepted for now; a `status_url` for polling real move status is a natural follow-up, out of scope here.

**Why swallow expected paste failures in the task:** the worker's generic exception handler retries up to `max_retries` and then reports to Sentry. A checked-out document (or a user lacking destination permission) will still fail identically on retry, so retrying is pointless, and reporting known "not reported" exceptions to Sentry contradicts why they were made "not reported" in the first place.

## Verification

**Commands:**
- `bin/test opengever.base.tests.test_security opengever.bgtasks opengever.api.tests.test_move opengever.dossier.tests.test_move_items` -- expected: all pass
- `python -c "from opengever.bgtasks.move import MoveObjectsTask"` -- expected: no ImportError

**Manual checks (if no CLI):**
- With bgtasks enabled, moving an item via the classic UI shows the "queued" message and a `background_tasks` row with `task_type='move-objects'` appears; the item moves to the destination once a worker processes it. Moving as a user without Add permission at the destination results in the task failing silently (logged, not retried) rather than the item ending up in an unauthorized location.

## Suggested Review Order

**Security context: why the worker can't just run as `system`**

- `run_as_user()`: switches to the given user's real permissions, restoring the previous manager afterward — sibling to the pre-existing `elevated_privileges()` just above it, but deliberately *not* granting extra roles.
  [`security.py:90`](../../opengever/base/security.py#L90)

- `MoveObjectsTask.execute()`: resolves the queuing user, wraps `acl_users` and pastes only inside `run_as_user(...)` — fails closed (no paste) if the user can't be resolved.
  [`move.py:26`](../../opengever/bgtasks/move.py#L26)

- Acquisition-wraps the resolved real user and catches `Unauthorized` alongside the OFS copy/lock errors — both added after round-2 review found gaps unique to running as a real user.
  [`move.py:71`](../../opengever/bgtasks/move.py#L71)

- Proves the security manager genuinely switches identity during paste and is restored afterward — the test that would have caught the original gap.
  [`test_move.py:126`](../../opengever/bgtasks/tests/test_move.py#L126)

**Enqueue wiring: two call sites, same pattern**

- `Move.reply()`: groups sources by parent as before, but now enqueues (or pastes inline if OGDS isn't ready) instead of pasting directly; responds 202 with predicted target paths.
  [`move.py:48`](../../opengever/api/move.py#L48)

- `MoveItemsForm.handle_submit()`: cut stays synchronous per item; only the paste is deferred, with the `admin_unit is None` fallback keeping its original per-exception-type handling.
  [`move_items.py:109`](../../opengever/dossier/move_items.py#L109)

- `MoveItemForm` (single-item view) is deliberately untouched — still says "was moved", a known follow-up inconsistency, not silently expanded in scope here.
  [`move_items.py:268`](../../opengever/dossier/move_items.py#L268)

**Task implementation**

- `paste_clipboard()`: the thin, single-purpose wrapper both the synchronous fallback and the task itself call — keeps the diff between "paste now" and "paste later" minimal.
  [`move.py:16`](../../opengever/bgtasks/move.py#L16)

**Tests**

- Enqueue tests confirm task grouping (API: per parent, form: per item) and that `user_id` travels with every queued task.
  [`test_move.py:43`](../../opengever/bgtasks/tests/test_move.py#L43)

- `assert_can_move` now expects `202` instead of `200`, the one status-code ripple into the pre-existing REST test suite.
  [`test_move.py:25`](../../opengever/api/tests/test_move.py#L25)
