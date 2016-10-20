SCHEMA_DUMPS_DIR = 'docs/schema-dumps'
SCHEMA_DOCS_DIR = 'docs/public/api/schemas'


GEVER_TYPES = [
    'opengever.dossier.businesscasedossier',
    'opengever.document.document',
    'ftw.mail.mail',
    'opengever.contact.contact',
    'opengever.repository.repositoryfolder',
    'opengever.repository.repositoryroot',
]

GEVER_SQL_TYPES = [
    '_opengever.contact.models.Address',
    '_opengever.contact.models.MailAddress',
    '_opengever.contact.models.OrgRole',
    '_opengever.contact.models.Organization',
    '_opengever.contact.models.Person',
    '_opengever.contact.models.PhoneNumber',
    '_opengever.contact.models.URL',
    '_opengever.ogds.models.user.User',
    '_opengever.ogds.models.group.Group',
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
