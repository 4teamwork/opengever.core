---
title: 'Background Tasks Kill Switch'
type: 'feature'
created: '2026-07-02'
status: 'done'
baseline_commit: 'd9734e90b235ca0db8e7eebfc96d7d5a17ce7833'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `queue_task()` always enqueues a DB row for the `BackgroundTaskWorker` to process out-of-band. There's no way to disable background processing, and in tests (where no worker runs) queued tasks never execute before assertions run, which will silently break any test that depends on a task's side effect (e.g. `reindexObjectSecurity`'s now-async security reindex).

**Approach:** Add a Plone registry boolean `opengever.bgtasks.interfaces.IBackgroundTaskSettings.is_feature_enabled` (default `True`). When disabled, `queue_task()` runs the task handler synchronously instead of enqueueing a DB row. Wire it into `IntegrationTestCase` as a feature flag (`FEATURE_FLAGS['bgtasks']`), disabled by default in `setUp()`, re-enabled per-test via `features = ('bgtasks',)` for tests that specifically exercise queueing/worker behavior.

## Boundaries & Constraints

**Always:**
- If the registry record can't be read (no site, missing record, any error), treat background tasks as **disabled** (fail-safe = synchronous execution).
- `queue_task()` still raises `ValueError` for an unregistered `task_type` regardless of the flag.
- Synchronous fallback calls the same `handler.execute(task, commit_checkpoint)` path used by the worker, with a no-op `commit_checkpoint`, so task handler code doesn't need to special-case sync vs async.
- `IntegrationTestCase.setUp()` disables `bgtasks` by default (same pattern as `deactivate_extjs`), so tests unrelated to bgtasks keep synchronous, pre-existing behavior.
- Tests in `opengever/bgtasks/tests/` that assert on actual queueing/worker behavior must keep the feature enabled: `TestReindexObjectSecurityPatch` via `features = ('bgtasks',)`; `TestBackgroundTaskModel` (plain `unittest.TestCase`, no Plone site, so the registry read always fails) via mocking `opengever.bgtasks.task.is_background_tasks_enabled` to return `True` in `setUp`.

**Ask First:** none anticipated.

**Never:** Do not change `BackgroundTaskWorker`/`runner.py` — the flag only affects `queue_task()`'s enqueue-vs-execute decision, not the worker loop itself.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Flag enabled (default) | registry record `True` or unset (schema default) | `queue_task()` creates a pending `BackgroundTask` row via `session.add`, returns it | N/A |
| Flag disabled | registry record `False` | `queue_task()` looks up the handler class, calls `execute(task, noop_checkpoint)` synchronously, returns the (unpersisted) task object | Exception from `execute()` propagates to caller, same as it would for whatever code path the caller previously used before bgtasks existed |
| Registry unreadable | no Plone site / record missing / lookup raises | Treated as disabled → synchronous execution | Exception from the registry read itself is swallowed; only the read, not the task execution |
| Unknown task type | `task_type not in _task_registry` | `ValueError` raised before any flag check | N/A |

</frozen-after-approval>

## Code Map

- `opengever/bgtasks/interfaces.py` -- new file, `IBackgroundTaskSettings.is_feature_enabled` (Bool, default `True`)
- `opengever/core/profiles/default/registry.xml` -- register the new interface's records (alphabetical, new `<!-- BGTASKS -->` section)
- `opengever/bgtasks/task.py` -- add `is_background_tasks_enabled()` helper; branch `queue_task()` on it
- `opengever/testing/integration_test_case.py` -- add `'bgtasks'` to `FEATURE_FLAGS`; add `deactivate_background_tasks()` (mirrors `deactivate_extjs()`) called unconditionally in `setUp()`
- `opengever/bgtasks/tests/test_reindex_object_security.py` -- `TestReindexObjectSecurityPatch` gets `features = ('bgtasks',)`
- `opengever/bgtasks/tests/test_model.py` -- `TestBackgroundTaskModel.setUp()` patches `is_background_tasks_enabled` to `True` (no Plone site available in this layer)
- `opengever/bgtasks/tests/test_task.py` -- new file, unit tests for the disabled/enabled/unreadable-registry branches of `queue_task()`

## Tasks & Acceptance

**Execution:**
- [x] `opengever/bgtasks/interfaces.py` -- create `IBackgroundTaskSettings` with `is_feature_enabled = schema.Bool(default=True)` -- defines the registry record
- [x] `opengever/core/profiles/default/registry.xml` -- add `<records interface="opengever.bgtasks.interfaces.IBackgroundTaskSettings" />` -- registers the record so `api.portal.get/set_registry_record` works
- [x] `opengever/bgtasks/task.py` -- add `is_background_tasks_enabled()` (try `api.portal.get_registry_record(...)`, except `Exception` return `False`); in `queue_task()`, build the `BackgroundTask` object first, then branch: enabled → `session.add(task)` (current behavior); disabled → `get_task_class(task_type)().execute(task, lambda data: None)` -- implements the kill switch
- [x] `opengever/testing/integration_test_case.py` -- add `'bgtasks': 'opengever.bgtasks.interfaces.IBackgroundTaskSettings.is_feature_enabled'` to `FEATURE_FLAGS`; add `deactivate_background_tasks()` method (docstring pointing to `self.activate_feature('bgtasks')`); call it in `setUp()` next to `self.deactivate_extjs()` -- makes sync execution the test default
- [x] `opengever/bgtasks/tests/test_reindex_object_security.py` -- add `features = ('bgtasks',)` to `TestReindexObjectSecurityPatch` -- keeps its queueing assertions valid
- [x] `opengever/bgtasks/tests/test_model.py` -- patch `opengever.bgtasks.task.is_background_tasks_enabled` to return `True` in `TestBackgroundTaskModel.setUp()` via `mock.patch(...).start()` + `self.addCleanup(...)` -- keeps existing queueing assertions valid despite no Plone site
- [x] `opengever/bgtasks/tests/test_task.py` -- new tests: enabled (default) queues a row; disabled executes synchronously and returns a task with no DB row created; registry read raising falls back to disabled/synchronous; unknown task type still raises `ValueError` regardless of flag -- covers the I/O matrix

**Acceptance Criteria:**
- Given the registry flag is at its schema default (unset), when `queue_task()` is called, then a pending `BackgroundTask` row is created (current behavior unchanged).
- Given the registry flag is `False`, when `queue_task()` is called with a registered task type, then no DB row is created and the handler's `execute()` runs synchronously before `queue_task()` returns.
- Given an `IntegrationTestCase` subclass without `features = ('bgtasks',)`, when code under test triggers `reindexObjectSecurity()`, then the security reindex happens synchronously within the test (no leftover pending task).
- Given `TestReindexObjectSecurityPatch` and `TestBackgroundTaskModel`, when their existing tests run, then all currently-passing assertions about queueing/pending rows still pass unmodified.

## Spec Change Log

## Verification

**Commands:**
- `bin/test -m opengever.bgtasks` -- expected: all bgtasks tests pass, including new `test_task.py`
- `bin/test -m opengever.base -t test_reindex` (or nearest equivalent covering other `reindexObjectSecurity`-triggering integration tests, if any run in CI scope) -- expected: no new failures caused by the default-disabled flag

## Suggested Review Order

**Kill switch logic**

- Entry point — the fail-safe check driving the whole feature; unreadable registry means disabled.
  [`task.py:28`](../../opengever/bgtasks/task.py#L28)

- Branch point in `queue_task()` — enabled enqueues as before, disabled runs the handler inline.
  [`task.py:62`](../../opengever/bgtasks/task.py#L62)

- `task_id` is now set eagerly so both branches return a task with a valid id.
  [`task.py:49`](../../opengever/bgtasks/task.py#L49)

**Registry wiring**

- New settings interface backing the flag, default `True`.
  [`interfaces.py:7`](../../opengever/bgtasks/interfaces.py#L7)

- Registers the record so `get/set_registry_record` can read/write it.
  [`registry.xml:19`](../../opengever/core/profiles/default/registry.xml#L19)

**Test harness default**

- `bgtasks` added as a feature flag other `IntegrationTestCase` tests can toggle.
  [`integration_test_case.py:113`](../../opengever/testing/integration_test_case.py#L113)

- Disabled unconditionally in `setUp()`, mirroring `deactivate_extjs()`, so unrelated tests stay synchronous.
  [`integration_test_case.py:144`](../../opengever/testing/integration_test_case.py#L144)

- The new method itself, with the rationale and reactivation hint in its docstring.
  [`integration_test_case.py:302`](../../opengever/testing/integration_test_case.py#L302)

**Peripherals**

- `TestReindexObjectSecurityPatch` opts back into real queueing to keep its assertions valid.
  [`test_reindex_object_security.py:16`](../../opengever/bgtasks/tests/test_reindex_object_security.py#L16)

- `TestBackgroundTaskModel` has no Plone site, so it force-enables the flag via mock instead.
  [`test_model.py:35`](../../opengever/bgtasks/tests/test_model.py#L35)

- New coverage for the enabled/disabled/unreadable-registry/unknown-type branches.
  [`test_task.py:23`](../../opengever/bgtasks/tests/test_task.py#L23)
