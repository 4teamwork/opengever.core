INDEXES = (
    ('filing_no', 'FieldIndex'),
    ('searchable_filing_no', 'ZCTextIndex', {'index_type': 'Okapi BM25 Rank',
                                             'lexicon_id': 'plone_lexicon'}),
)
