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

GEVER_TYPES_TO_OGGBUNDLE_TYPES = {
    'opengever.document.document': 'document',
    'opengever.dossier.businesscasedossier': 'dossier',
    'opengever.repository.repositoryfolder': 'repofolder',
    'opengever.repository.repositoryroot': 'reporoot',
}

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
    'opengever.task.task.ITask': {
        'issuer': u'<G\xfcltige User-ID>',
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
    'opengever.task.task.ITask': {
        'deadline': u'<Aktuelles Datum>',
    },
}

# Dropped from all schema dumps
IGNORED_FIELDS = [
    'plone.app.versioningbehavior.behaviors.IVersionable.changeNote',
    'opengever.document.behaviors.metadata.IDocumentMetadata.digitally_available',
    'opengever.document.behaviors.metadata.IDocumentMetadata.preview',
    'opengever.document.behaviors.metadata.IDocumentMetadata.thumbnail',
    'opengever.dossier.behaviors.dossier.IDossier.temporary_former_reference_number',  # noqa
]

# Dropped from OGGBundle schema dumps
IGNORED_OGGBUNDLE_FIELDS = {
    'document': ['file', 'archival_file', 'archival_file_state'],
}

JSON_SCHEMA_FIELD_TYPES = {
    'TextLine':      {'type': 'string'},                     # noqa
    'Text':          {'type': 'string'},                     # noqa
    'Tuple':         {'type': 'array'},                      # noqa
    'Date':          {'type': 'string', 'format': 'date'},   # noqa
    'Float':         {'type': 'number'},                     # noqa
    'Int':           {'type': 'integer'},                    # noqa
    'RelationList':  {'type': 'array'},                      # noqa
    'Bool':          {'type': 'boolean'},                    # noqa
    'NamedBlobFile': {'type': 'string'},                     # noqa
    'Choice':        {'type': 'string'},                     # noqa
    'NamedImage':    {'type': 'string'},                     # noqa
    'List':          {'type': 'array'},                      # noqa
    'URI':           {'type': 'string', 'format': 'uri'},    # noqa
}

PYTHON_TO_JS_TYPES = {
    int: 'integer',
    unicode: 'string',
    str: 'string',
}
