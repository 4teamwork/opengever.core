# Deferred Work

## From: background-tasks-infrastructure (2026-06-12)

- **datetime.now() vs UTC across worker**: All timestamps use naive `datetime.now()`. Pre-existing pattern in opengever (nightly jobs same). Consider switching to `datetime.utcnow()` uniformly to avoid TZ drift on DST changes. Low risk in practice since server and DB are usually in same timezone.

- **_task_registry test isolation**: Module-level `_task_registry` dict accumulates registrations across the test session. If two tests register conflicting type names, the last-imported wins silently. Add cleanup or use per-test override pattern.

- **register_task_type silent overwrite**: `register_task_type(name, cls)` silently replaces an existing entry. Consider raising `ValueError` on duplicate registration to catch accidental double-imports early.

- **Unknown task_type error type inconsistency**: `queue_task` raises `ValueError` for unknown types; `get_task_class` raises `KeyError`. A task whose type becomes unregistered after enqueue will fail with a `KeyError` — caught as a task failure but the error message gives no hint it's a code deployment issue vs data issue.

- **Checkpoint commit failure isolation**: If `commit_checkpoint` raises inside `execute()`, the outer `except Exception` catches it, aborts, and resets the task to the last committed state. The spec says "checkpoint abort only affects that commit" but in practice the abort rolls back to before the task was marked running. Acceptable but worth documenting.

- **Multi-site worker support**: `run_background_tasks_handler` uses `get_first_plone_site` because `run_forever` is an infinite loop. If opengever ever needs a multi-site worker, restructure so `run_forever` processes one task per call and the outer loop drives the forever behaviour.
