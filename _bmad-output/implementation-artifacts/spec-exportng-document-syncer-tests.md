---
title: 'Exportng document syncer tests'
type: 'chore'
created: '2026-11-12'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The `DocumentSyncer` in `opengever.exportng.catalog` has no tests, and all syncer tests live in one file, `test_catalog_syncer.py`.

**Approach:** Add document syncer tests based on `SyncerTestMixin` (from the previous commit) and put each syncer's tests in its own file, e.g. `test_dossier_syncer.py` and `test_document_syncer.py`.

</frozen-after-approval>

## Implementation Notes

- `test_catalog_syncer.py` renamed to `test_dossier_syncer.py` (`git mv`, content unchanged).
- Added `test_document_syncer.py` with `TestDocumentSyncer` and a `document_row()` helper. It expects 41 rows, mails included.
- The expected values were taken from a run of the current serializer and then checked against the fixture. They are a golden master, not independently derived.
- `object_to_delete` is `expired_document`. Deleting `self.document` also modifies a related document, which breaks the "other rows unchanged" check.
- Not covered: `document_versions` and `journal_entries` tables (the mixin only reads the main table).
- Observed, not changed: template titles come out mojibake in `objname`, and template, private-folder and workspace documents are exported because the query filters only on portal type and `trashed`.
- Verified: `bin/test -m opengever.exportng` runs 12 tests, all pass. isort is clean.
- No towncrier entry: no ticket ID known.
