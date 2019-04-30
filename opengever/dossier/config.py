INDEXES = (
    ('is_subdossier', 'BooleanIndex'),
    ('containing_subdossier', 'FieldIndex'),
    ('containing_dossier', 'FieldIndex'),
    ('retention_expiration', 'DateIndex'),
    ('external_reference', 'FieldIndex'),
    ('blocked_local_roles', 'BooleanIndex'),
    ('after_resolve_jobs_pending', 'BooleanIndex'),
)
