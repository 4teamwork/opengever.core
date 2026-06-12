---
title: 'Background Tasks Infrastructure'
type: 'feature'
created: '2026-06-12'
status: 'done'
baseline_commit: 'f07394dbf3b7914f51f464ae2490fdd3663d57d1'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Long-running operations block the request cycle and can't be deferred, scheduled, or resumed after a process restart — nightly jobs cover scheduled batch work but lack a general-purpose, always-on execution queue.

**Approach:** Introduce `opengever.bgtasks`, a new package that stores tasks in a new OGDS SQL table, provides a base class for implementing task handlers, and runs an endless worker process (zopectl command) that claims and executes tasks from the queue with priority ordering, scheduled execution, retry logic, and intermediate-commit checkpointing.

## Boundaries & Constraints

**Always:**
- Python 2.7 compatible throughout; use `u''` string literals, `super(Cls, self)`, `%`-formatting.
- SQL table lives in the OGDS database; all column names/constraints ≤ 30 chars (Oracle limit).
- Use constants from `opengever.base.model` for column lengths (`UNIT_ID_LENGTH`, `UID_LENGTH`).
- Per-admin-unit queue: tasks are scoped to `admin_unit_id`; worker only processes tasks for the current admin unit.
- Single worker guaranteed — no distributed locking needed.
- GenericSetup upgrade step (`SchemaMigration` subclass) creates the table; never create it in the model definition.
- All new table names added to `tables` list in `opengever/base/model/__init__.py`.
- Constraint names ≤ 30 chars; avoid PostgreSQL-specific syntax.

**Ask First:**
- Any change to the SQL schema beyond what is specified here (additional columns, indexes, FK constraints).
- Adding Zope adapter/utility registrations beyond what is needed for the worker to run.

**Never:**
- Celery or any external task queue library.
- Running tasks in threads or subprocesses within the worker.
- Reading from the ZODB inside the upgrade step.
- Using ORM model imports inside upgrade step code.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Enqueue immediate task | `queue_task(task_type, args, priority=5)` | Row inserted with `status='pending'`, `scheduled_for=NULL` | Raise `ValueError` for unknown task_type |
| Enqueue scheduled task | `queue_task(..., run_at=datetime)` | Row inserted with `scheduled_for=run_at` | Same |
| Worker picks next task | `status='pending'`, `scheduled_for <= now` OR NULL, lowest priority int first | Task marked `status='running'`, `started=now()` | Skip tasks with future `scheduled_for` |
| Task succeeds | `execute()` returns | `status='succeeded'`, `finished=now()`, commit | — |
| Task fails, retries left | `execute()` raises, `retries < max_retries` | `retries += 1`, `status='pending'`, `error_message` set | Transaction aborted, row re-queued |
| Task fails, no retries | `execute()` raises, `retries >= max_retries` | `status='failed'`, `error_message` set, commit | Logged to Sentry |
| Intermediate commit | Task calls `commit_checkpoint(data)` | `checkpoint_data` JSON-serialized and committed | Exception during checkpoint aborts only that commit |
| Worker restart with running task | `status='running'` rows found on startup | Reset to `status='pending'` (checkpoint_data preserved) | — |
| No pending tasks | Queue empty | Worker sleeps 5s before next poll | — |

</frozen-after-approval>

## Code Map

- `opengever/bgtasks/__init__.py` — namespace package init
- `opengever/bgtasks/configure.zcml` — includes `.upgrades` sub-package
- `opengever/bgtasks/model.py` — `BackgroundTask` SQLAlchemy model (`background_tasks` table)
- `opengever/bgtasks/task.py` — `BaseBackgroundTask` base class + `_task_registry` dict + `queue_task()` helper
- `opengever/bgtasks/worker.py` — `BackgroundTaskWorker` class (endless loop, claim, execute, checkpoint)
- `opengever/bgtasks/cronjobs.py` — `run_background_tasks_handler(app, args)` zopectl command entry point
- `opengever/bgtasks/upgrades/__init__.py` — empty
- `opengever/bgtasks/upgrades/configure.zcml` — registers GenericSetup profile + upgrade step
- `opengever/bgtasks/upgrades/20260612000000_add_background_tasks_table/upgrade.py` — `SchemaMigration` that creates the table
- `opengever/bgtasks/profiles/default/metadata.xml` — empty metadata (no dependencies)
- `opengever/bgtasks/tests/__init__.py` — empty
- `opengever/bgtasks/tests/test_model.py` — unit tests for model querying and status transitions
- `opengever/bgtasks/tests/test_worker.py` — unit tests for worker: claim logic, retry logic, checkpoint, restart recovery
- `opengever/base/model/__init__.py` — add `'background_tasks'` to `tables` list (line ~36–46)
- `setup.py` — add `run_background_tasks = opengever.bgtasks.cronjobs:run_background_tasks_handler` to `[zopectl.command]`

## Tasks & Acceptance

**Execution:**
- [x] `opengever/bgtasks/__init__.py` -- create empty namespace init
- [x] `opengever/bgtasks/model.py` -- define `BackgroundTask` SQLAlchemy model with columns: `task_id` (String(36) PK), `admin_unit_id` (String(30)), `task_type` (String(100)), `status` (String(20), default `u'pending'`), `priority` (Integer, default 5), `scheduled_for` (DateTime nullable), `created` (DateTime), `started` (DateTime nullable), `finished` (DateTime nullable), `retries` (Integer default 0), `max_retries` (Integer default 3), `error_message` (UnicodeCoercingText nullable), `checkpoint_data` (UnicodeCoercingText nullable), `task_arguments` (UnicodeCoercingText nullable)
- [x] `opengever/bgtasks/task.py` -- define `BaseBackgroundTask` with `task_type = None` class attr, `execute(task, commit_checkpoint)` abstract method; module-level `_task_registry = {}`, `register_task_type(name, cls)`, `get_task_class(name)`; `queue_task(task_type, admin_unit_id, arguments=None, priority=5, run_at=None, max_retries=3)` that inserts a new `BackgroundTask` row with a UUID `task_id` and `created=datetime.now()`
- [x] `opengever/bgtasks/worker.py` -- define `BackgroundTaskWorker` with: `reset_interrupted_tasks(admin_unit_id)` (set status=pending for all running rows); `claim_next_task(admin_unit_id)` (query pending, scheduled_for<=now or null, order by priority ASC then created ASC, return first); `execute_task(task)` (set status=running, call handler's execute with commit_checkpoint closure, on success set status=succeeded, on exception handle retries); `commit_checkpoint(task, data)` (JSON-serialize data into task.checkpoint_data, commit); `run_forever(admin_unit_id)` (call reset_interrupted_tasks, loop: claim→execute or sleep 5s)
- [x] `opengever/bgtasks/cronjobs.py` -- implement `run_background_tasks_handler(app, args)` following the `run_nightly_jobs_handler` pattern: install Sentry excepthook, setup logger, iterate `all_plone_sites(app)`, call `setup_plone(plone_site)`, get current admin unit ID from registry, instantiate and call `worker.run_forever(admin_unit_id)`
- [x] `opengever/bgtasks/upgrades/configure.zcml` -- register `opengever.bgtasks:default` GenericSetup profile and register upgrade step class `AddBackgroundTasksTable` (source=`*`, destination=`1001`, profile=`opengever.bgtasks:default`)
- [x] `opengever/bgtasks/upgrades/20260612000000_add_background_tasks_table/upgrade.py` -- `SchemaMigration` subclass `AddBackgroundTasksTable` with `profileid='opengever.bgtasks'`, `upgradeid=1001`; `migrate()` calls `self.op.create_table('background_tasks', ...)` with all columns matching the model; use raw SQLAlchemy column types (not ORM model); check `if 'background_tasks' in self.metadata.tables` first to make it re-runnable
- [x] `opengever/bgtasks/profiles/default/metadata.xml` -- empty `<metadata/>` file
- [x] `opengever/bgtasks/configure.zcml` -- minimal configure including `.upgrades`
- [x] `opengever/base/model/__init__.py` -- append `'background_tasks'` to `tables` list
- [x] `setup.py` -- add `run_background_tasks = opengever.bgtasks.cronjobs:run_background_tasks_handler` in `[zopectl.command]` section
- [x] `opengever/bgtasks/tests/test_model.py` -- test `queue_task()` creates correct row; test `BackgroundTask.query` filters by admin_unit_id and status; test priority/scheduled_for ordering
- [x] `opengever/bgtasks/tests/test_worker.py` -- test `reset_interrupted_tasks` resets running→pending; test `claim_next_task` respects priority, skips future scheduled tasks; test retry increment on failure; test `status='failed'` when max_retries exhausted; test `commit_checkpoint` persists data; test full execute→succeeded flow

**Acceptance Criteria:**
- Given a new `opengever.bgtasks` package, when Plone loads ZCML, then `background_tasks` table exists and `BackgroundTask.query` is functional.
- Given two pending tasks with different priorities, when the worker claims the next task, then the lower-priority integer wins (runs first).
- Given a task with `scheduled_for` in the future, when the worker polls, then the task is not claimed.
- Given a task whose `execute()` raises, when `retries < max_retries`, then the task is re-queued with `retries` incremented and `status='pending'`.
- Given a task whose `execute()` raises and `retries == max_retries`, then `status` is set to `'failed'` and `error_message` records the traceback.
- Given a task calls `commit_checkpoint(data)`, when the worker process is killed and restarted, then the task is re-queued with `checkpoint_data` intact so the handler can resume.
- Given the worker starts with a `status='running'` task (leftover from crash), then it resets it to `status='pending'` before processing.
- Given `bin/instance run_background_tasks` is executed, then the worker runs continuously without requiring manual intervention.

## Design Notes

**Task type registry** — a plain module-level dict rather than a Zope adapter avoids ZCML boilerplate for task registration. Task implementors call `register_task_type('my-type', MyTask)` at module import time (similar to how content type registration works in ftw.builder).

**Checkpoint pattern** — the `commit_checkpoint(data)` closure passed to `execute()` serializes `data` to JSON, stores it in `task.checkpoint_data`, and calls `transaction.commit()`. On the next `execute()` invocation after a restart, the handler reads `task.checkpoint_data` (JSON-parsed) to resume. This keeps the resume logic in the task handler, not the worker.

**Upgrade step re-entrancy** — guard with `if 'background_tasks' not in self.metadata.tables` before calling `create_table` so re-running the upgrade is a no-op.

## Verification

**Commands:**
- `bin/test opengever/bgtasks/tests/` -- expected: all tests pass
- `python -c "from opengever.bgtasks.model import BackgroundTask"` -- expected: no ImportError

**Manual checks (if no CLI):**
- After installing the GenericSetup profile, verify `background_tasks` table exists in the database with all expected columns.
- Run `bin/instance run_background_tasks` and confirm the worker starts and logs "No pending tasks" (or processes any queued task).

## Suggested Review Order

**Design intent**

- SQL model: columns, status constants, priority default, ORM query helpers
  [`model.py:42`](../../opengever/bgtasks/model.py#L42)

- Task registry + `queue_task()`: UUID assignment, arguments JSON, validation
  [`task.py:24`](../../opengever/bgtasks/task.py#L24)

- `BaseBackgroundTask`: contract for implementors, checkpoint/arguments helpers
  [`task.py:48`](../../opengever/bgtasks/task.py#L48)

**Worker execution**

- `run_forever`: startup reset then claim→execute→sleep loop
  [`worker.py:29`](../../opengever/bgtasks/worker.py#L29)

- `claim_next_task`: WHERE + ORDER BY — how priority and scheduling are enforced
  [`worker.py:57`](../../opengever/bgtasks/worker.py#L57)

- `execute_task`: mark running, execute handler, re-fetch after abort, handle errors
  [`worker.py:70`](../../opengever/bgtasks/worker.py#L70)

- `commit_checkpoint` closure: intermediate commit pattern for resume-after-restart
  [`worker.py:79`](../../opengever/bgtasks/worker.py#L79)

- `_handle_failure`: retry re-queue vs permanent failure + Sentry notification
  [`worker.py:109`](../../opengever/bgtasks/worker.py#L109)

- `reset_interrupted_tasks`: startup recovery of running→pending on worker restart
  [`worker.py:41`](../../opengever/bgtasks/worker.py#L41)

**Schema migration**

- `AddBackgroundTasksTable`: re-entrant SchemaMigration creates the table
  [`upgrade.py:9`](../../opengever/bgtasks/upgrades/20260612000000_add_background_tasks_table/upgrade.py#L9)

- Upgrade step ZCML registration and directory auto-discovery
  [`upgrades/configure.zcml:1`](../../opengever/bgtasks/upgrades/configure.zcml#L1)

**Entry point**

- zopectl command: logger setup, Sentry hook, admin unit resolution, worker start
  [`cronjobs.py:51`](../../opengever/bgtasks/cronjobs.py#L51)

**Supporting changes**

- `'background_tasks'` appended to the OGDS tables list
  [`model/__init__.py:38`](../../opengever/base/model/__init__.py#L38)

- `run_background_tasks` zopectl command registered
  [`setup.py:205`](../../setup.py#L205)

**Tests**

- Worker: execution, retry, checkpoint, and restart recovery scenarios
  [`test_worker.py:50`](../../opengever/bgtasks/tests/test_worker.py#L50)

- Model: `queue_task`, admin-unit scoping, priority ordering
  [`test_model.py:28`](../../opengever/bgtasks/tests/test_model.py#L28)
