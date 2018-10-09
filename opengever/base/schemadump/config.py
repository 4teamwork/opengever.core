# noqa
SCHEMA_DUMPS_DIR = 'docs/schema-dumps'
SCHEMA_DOCS_DIR = 'docs/public/dev-manual/api/schemas'


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

# Workflow states allowed in JSON schemas. The state that's listed first
# indicates the initial workflow state (i.e. default state).
#
# Many workflow states are disabled here because we don't support migrating
# objects in these states from OGGBundle at this point.
ALLOWED_REVIEW_STATES = {
    'opengever.repository.repositoryroot': [
        'repositoryroot-state-active',
    ],
    'opengever.repository.repositoryfolder': [
        'repositoryfolder-state-active',
        # 'repositoryfolder-state-inactive',
    ],
    'opengever.dossier.businesscasedossier': [
        'dossier-state-active',
        # 'dossier-state-archived',
        # 'dossier-state-inactive',
        'dossier-state-resolved',
        # 'dossier-state-offered',
    ],
    'opengever.document.document': [
        'document-state-draft',
        # 'document-state-removed',
        # 'document-state-shadow',
    ],
    'ftw.mail.mail': [
        'mail-state-active',
        # 'mail-state-removed',
    ],
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

SEQUENCE_NUMBER_LABELS = {
    'opengever.document.document': u'Fortlaufend gez\xe4hlte Nummer eines Dokumentes.',  # noqa
    'opengever.dossier.businesscasedossier': u'Fortlaufend gez\xe4hlte Nummer eines Dossiers.',  # noqa
}

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
    'opengever.mail.mail.IMail.message_source',
    'opengever.dossier.behaviors.protect_dossier.IProtectDossier.reading',
    'opengever.dossier.behaviors.protect_dossier.IProtectDossier.reading_and_writing',
    'opengever.dossier.behaviors.protect_dossier.IProtectDossier.dossier_manager',

]

# Dropped from OGGBundle schema dumps
IGNORED_OGGBUNDLE_FIELDS = {
    'document': ['file', 'archival_file', 'archival_file_state'],
}


JSON_SCHEMA_FIELD_TYPES = {
    # Ugly, but need to wrap this because pycodestyle ignores noqa for E241
    'TextLine': {
        'type': 'string'},
    'Text': {
        'type': 'string'},
    'Tuple': {
        'type': 'array'},
    'Date': {
        'type': 'string', 'format': 'date'},
    'Datetime': {
        'type': 'string', 'format': 'datetime'},
    'Float': {
        'type': 'number'},
    'Int': {
        'type': 'integer'},
    'RelationList': {
        'type': 'array'},
    'Bool': {
        'type': 'boolean'},
    'NamedBlobFile': {
        'type': 'string'},
    'Choice': {
        'type': 'string'},
    'NamedImage': {
        'type': 'string'},
    'List': {
        'type': 'array'},
    'URI': {
        'type': 'string', 'format': 'uri'},
}

PYTHON_TO_JS_TYPES = {
    int: 'integer',
    unicode: 'string',
    str: 'string',
}
