INDEXES = (
    ('delivery_date', 'DateIndex'),
    ('document_author', 'ZCTextIndex',
        {'index_type': 'Okapi BM25 Rank',
         'lexicon_id': 'plone_lexicon'}),
    ('checked_out', 'FieldIndex'),
    ('document_date', 'DateIndex'),
    ('document_type', 'FieldIndex'),
    ('receipt_date', 'DateIndex'),
    ('sortable_author', 'FieldIndex'),
    ('public_trial', 'FieldIndex'),
    ('filesize', 'FieldIndex'),
    ('file_extension', 'FieldIndex'),
)
