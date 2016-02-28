SCHEMA_DUMPS_DIR = 'docs/schema-dumps'
SCHEMA_DOCS_DIR = 'docs/api/schemas'


GEVER_TYPES = [
    'opengever.dossier.businesscasedossier',
    'opengever.document.document',
    'ftw.mail.mail',
    'opengever.contact.contact',
]


VOCAB_OVERRIDES = {
    'opengever.dossier.behaviors.dossier.IDossier': {
        'responsible': u'<G\xfcltige User-ID>',
    },
}

DEFAULT_OVERRIDES = {
    'opengever.dossier.behaviors.dossier.IDossier': {
        'start': '<Aktuelles Datum>',
    },
    'opengever.document.behaviors.metadata.IDocumentMetadata': {
        'document_date': '<Aktuelles Datum>',
    },
}
