INDEXES = (
    ('deadline', 'DateIndex'),
    ('date_of_completion', 'DateIndex'),
    ('responsible', 'FieldIndex'),
    ('issuer', 'FieldIndex'),
    ('task_type', 'FieldIndex'),
    ('assigned_client', "KeywordIndex"),
    ('client_id', "KeywordIndex"),
    ('sequence_number', 'FieldIndex'),
    ('is_subtask', 'BooleanIndex'),
    ('predecessor', 'FieldIndex'),
)
