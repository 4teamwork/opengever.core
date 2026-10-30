---
title: 'Gracefully shut down background task worker on SIGINT/SIGTERM'
type: 'feature'
created: '2026-10-30'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Pressing Ctrl-C terminates the background task worker with a KeyboardInterrupt traceback, possibly in the middle of a task.

**Approach:** Install SIGINT/SIGTERM handlers in `BackgroundTaskWorker.run_forever` that request a stop. The worker finishes the currently running task, then exits the loop and logs a clean shutdown. A second signal falls back to the original handler (forced termination).

</frozen-after-approval>

## Implementation Notes
Changed `opengever/bgtasks/worker.py` (stop event, SIGINT/SIGTERM handlers installed only on the main thread, interruptible idle sleep, handlers restored on exit) and added a test in `test_worker.py`. The Python 2.7 test environment is unavailable locally, so the test was not run; the loop logic was checked with a stubbed Python 3 harness.

## Review Triage Log

- high (fixed): `threading.main_thread()` is missing on Python 2.7; replaced with a `_MainThread` isinstance check.
- medium (fixed): `signal.signal` may return None; restore falls back to `SIG_DFL`.
- low (fixed): logging inside the signal handler removed; stop event cleared at start of `run_forever`; test restores handler via `addCleanup`.
- low (rejected): extra tests (SIGTERM, second signal, off-main-thread), logging style, `request_stop` docstring; not worth the added code.
- defer-worthy, not recorded: long-running tasks cannot observe the stop request; they block shutdown until finished. This is the intended "finish current task" behaviour.
- false: second-signal KeyboardInterrupt inside DB code is the pre-existing behaviour, and matches the intent.
