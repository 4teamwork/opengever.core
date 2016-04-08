SCHEMA_DUMPS_DIR = 'docs/schema-dumps'
SCHEMA_DOCS_DIR = 'docs/api/schemas'


GEVER_TYPES = [
    'opengever.dossier.businesscasedossier',
    'opengever.document.document',
    'ftw.mail.mail',
    'opengever.contact.contact',
    'opengever.repository.repositoryfolder',
    'opengever.repository.repositoryroot',
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
    'opengever.repository.behaviors.referenceprefix.IReferenceNumberPrefix': {
        'reference_number_prefix':
            u'<H\xf6chste auf dieser Ebene vergebene Nummer + 1>',
    },
}
