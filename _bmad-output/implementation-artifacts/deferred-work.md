# Deferred Work

## From: background-tasks-infrastructure (2026-06-12)

- **datetime.now() vs UTC across worker**: All timestamps use naive `datetime.now()`. Pre-existing pattern in opengever (nightly jobs same). Consider switching to `datetime.utcnow()` uniformly to avoid TZ drift on DST changes. Low risk in practice since server and DB are usually in same timezone.

- **_task_registry test isolation**: Module-level `_task_registry` dict accumulates registrations across the test session. If two tests register conflicting type names, the last-imported wins silently. Add cleanup or use per-test override pattern.

- **register_task_type silent overwrite**: `register_task_type(name, cls)` silently replaces an existing entry. Consider raising `ValueError` on duplicate registration to catch accidental double-imports early.

- **Unknown task_type error type inconsistency**: `queue_task` raises `ValueError` for unknown types; `get_task_class` raises `KeyError`. A task whose type becomes unregistered after enqueue will fail with a `KeyError` — caught as a task failure but the error message gives no hint it's a code deployment issue vs data issue.

- **Checkpoint commit failure isolation**: If `commit_checkpoint` raises inside `execute()`, the outer `except Exception` catches it, aborts, and resets the task to the last committed state. The spec says "checkpoint abort only affects that commit" but in practice the abort rolls back to before the task was marked running. Acceptable but worth documenting.

- **Multi-site worker support**: `run_background_tasks_handler` uses `get_first_plone_site` because `run_forever` is an infinite loop. If opengever ever needs a multi-site worker, restructure so `run_forever` processes one task per call and the outer loop drives the forever behaviour.

## From: reindex-object-security-background-task (2026-06-23)

- **RUNNING task not cancelled during dedup**: Deduplication only cancels PENDING tasks for the same UID. If a task for the same object is already RUNNING (worker mid-execution), a second PENDING task is still enqueued. Both execute sequentially, which is safe (second is a no-op) but wasteful. A RUNNING check would require holding a lock or a different status model.

- **Transaction abort silently loses reindex**: If the calling transaction is aborted after `reindexObjectSecurity` returns (exception later in same request), both the dedup-delete and the new enqueue are rolled back. The security reindex is silently lost — no pending task, no error. Solving this properly requires after-commit hooks, which is a larger architectural change.

- **No synchronous fallback when queue_task fails**: If the SQL session is unavailable when `reindexObjectSecurity` is called, `queue_task` raises and the exception propagates to the caller. There is no fallback to running the reindex synchronously. This is intentional (avoids silent inconsistency) but worth revisiting if DB failures become a concern.

## From: background-tasks-kill-switch (2026-07-02)

- **Scheduling/priority/checkpoint semantics are no-ops when disabled**: When background tasks are disabled, `queue_task()` executes the handler immediately regardless of `run_at`, `priority`, or `max_retries`, and `commit_checkpoint` is a no-op. This is intentional per spec (no worker exists to honor them when disabled), but no current caller passes `run_at`/relies on checkpointing, so it's untested territory. Worth a second look if a future task handler starts relying on scheduled execution or checkpoint resumption.
