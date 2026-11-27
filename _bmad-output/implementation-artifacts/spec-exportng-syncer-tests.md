---
title: 'Generic exportng syncer tests'
type: 'chore'
created: '2026-11-11'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `TestDossierSyncer` in `opengever/exportng/tests/test_catalog_syncer.py` is only a rough example. It does not verify that an initial sync exports all dossiers, that a later sync touches only modified dossiers, that deleted dossiers are marked `_deleted`, or that every exported attribute is correct.

**Approach:** Rewrite the test around a reusable base/mixin (table setup, helpers for reading rows, sync-run assertions) so other syncers can be tested the same way, and implement the dossier test on it.

</frozen-after-approval>

## Implementation Notes

- Added `opengever/exportng/tests/base.py` (`SyncerTestMixin`, hooks: `expected_rows`, `object_to_modify`/`modify`, `object_to_delete`) and rewrote `test_catalog_syncer.py` on top of it.
- `compose.yaml`: added `exportng-db` service and `EXPORTNG_DSN` for `ogcore-test`, since the layer cannot start docker inside the container. `layer.py` healthcheck now uses the DSN instead of `self.port`.
- Review layers skipped (no explicit permission to spawn subagents). Not committed.
- Verified: `bin/test -m opengever.exportng` 6 tests pass; isort clean.

## Review Triage Log

- Timezone-dependent expectations: low. The tests run in the pinned Docker image, where the TZ is fixed. Fixing it would add more than a simple correction. Rejected.
- Re-adding a soft-deleted object: medium, real, but already in `CatalogSyncer` and not caused by this change. `sql_items` filters out deleted rows, so a re-appearing key is treated as added. `create_table` defines no primary key, so the INSERT produces a duplicate row. Deferred.
- Deletion does not refresh `_modified_at`: low. Intended behaviour of `delete_objects`. Rejected.
- Coverage gaps (other syncers, additional tables, mail/forwarding, `has_many`/`ignore`): out of scope. The request covers the dossier syncer, with other syncers "later". Journal/remarks table checks deferred.
- Fragile design (string `syncer_class_name`, mutable `modified_columns`, `api` import inside `delete`): low. Rejected.
- DB state left behind after tests: low. `setUp` resets the tables. Rejected.
- Compose/layer duplication, healthcheck `KeyError`, `start_period`: low. Rejected.
- Missing towncrier entry: no ticket ID known. Left for the user.
- Untracked spec file: the user decides whether to commit it.
- `_modified_at` tz-aware vs naive comparison: false. The delta test passes, which shows `freeze` is applied consistently.
