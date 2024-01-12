# noqa
SCHEMA_DUMPS_DIR = 'docs/schema-dumps'
SCHEMA_DOCS_DIR = 'docs/public/dev-manual/api/schemas'


GEVER_TYPES = [
    'opengever.dossier.businesscasedossier',
    'opengever.document.document',
    'ftw.mail.mail',
    'opengever.contact.contact',
    'opengever.task.task',
    'opengever.repository.repositoryfolder',
    'opengever.repository.repositoryroot',
    'opengever.inbox.container',
    'opengever.inbox.inbox',
    'opengever.private.root',
    'opengever.dossier.templatefolder',
    'opengever.workspace.root',
    'opengever.workspace.workspace',
    'opengever.workspace.folder',
    'opengever.meeting.proposal',
    'opengever.workspace.meeting',
    'opengever.workspace.meetingagendaitem',
]

GEVER_TYPES_TO_OGGBUNDLE_TYPES = {
    'opengever.document.document': 'document',
    'opengever.dossier.businesscasedossier': 'dossier',
    'opengever.repository.repositoryfolder': 'repofolder',
    'opengever.repository.repositoryroot': 'reporoot',
    'opengever.inbox.container': 'inboxcontainer',
    'opengever.inbox.inbox': 'inbox',
    'opengever.private.root': 'privateroot',
    'opengever.dossier.templatefolder': 'templatefolder',
    'opengever.workspace.root': 'workspaceroot',
    'opengever.workspace.workspace': 'workspace',
    'opengever.workspace.folder': 'workspacefolder',
}

# Plural forms where just appending an 's' at the end is not enough
IRREGULAR_PLURALS = {
    'inbox': 'inboxes',
}

# Types that don't need a parent_guid / parent_reference during import, but
# instead will (always) be created directly below the Plone site root.
ROOT_TYPES = [
    'opengever.repository.repositoryroot',
    'opengever.workspace.root',
    'opengever.inbox.container',
    'opengever.private.root',
    'opengever.dossier.templatefolder',
]

# Types that may or may not be created directly below the Plone site root.
# Their schema supports parent pointers, but they are optional.
OPTIONAL_ROOT_TYPES = [
    'opengever.inbox.inbox',

]

# Types that can unambiguously be parented to an existing container, and
# therefore don't require a parent_guid / parent_reference
PARENTABLE_TYPES = [
    'opengever.workspace.workspace'
]

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
    'opengever.inbox.container': [
        'inbox-state-default',
    ],
    'opengever.inbox.inbox': [
        'inbox-state-default',
    ],
    'opengever.private.root': [
        'repositoryroot-state-active',  # [sic] WF definition contains typo
    ],
    'opengever.dossier.templatefolder': [
        'templatefolder-state-active',
    ],
    'opengever.workspace.root': [
        'opengever_workspace_root--STATUS--active',
    ],
    'opengever.workspace.workspace': [
        'opengever_workspace--STATUS--active',
    ],
    'opengever.workspace.folder': [
        'opengever_workspace_folder--STATUS--active',
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

ROLES_BY_SHORTNAME = {
    'read': 'Reader',
    'add': 'Contributor',
    'edit': 'Editor',
    'close': 'Reviewer',
    'reactivate': 'Publisher',
    'manage_dossiers': 'DossierManager',
    'workspaces_creator': 'WorkspacesCreator',
    'workspaces_user': 'WorkspacesUser',
    'workspace_admin': 'WorkspaceAdmin',
    'workspace_member': 'WorkspaceMember',
    'workspace_guest': 'WorkspaceGuest',
}

# Inverted mapping of the above
SHORTNAMES_BY_ROLE = {v: k for k, v in ROLES_BY_SHORTNAME.iteritems()}

DEFAULT_MANAGEABLE_ROLES = [
    'read',
    'add',
    'edit',
    'close',
    'reactivate',
]

MANAGEABLE_ROLES_BY_TYPE = {
    'opengever.repository.repositoryroot':
        DEFAULT_MANAGEABLE_ROLES + ['manage_dossiers'],
    'opengever.repository.repositoryfolder':
        DEFAULT_MANAGEABLE_ROLES + ['manage_dossiers'],
    'opengever.workspace.root':
        ['workspaces_creator', 'workspaces_user'],
    'opengever.workspace.workspace':
        ['workspace_admin', 'workspace_member', 'workspace_guest'],
    'opengever.workspace.folder':
        ['workspace_admin', 'workspace_member', 'workspace_guest'],
}


GEVER_SQL_TYPES = [
    '_opengever.ogds.models.user.User',
    '_opengever.ogds.models.group.Group',
]

GEVER_SQL_TYPES_TO_OGGBUNDLE_TYPES = {
    '_opengever.ogds.models.user.User': 'ogds_user',
}


SEQUENCE_NUMBER_LABELS = {
    'opengever.document.document': u'Fortlaufend gez\xe4hlte Nummer eines Dokumentes.',  # noqa
    'opengever.dossier.businesscasedossier': u'Fortlaufend gez\xe4hlte Nummer eines Dossiers.',  # noqa
}

VOCAB_OVERRIDES = {
    'opengever.dossier.behaviors.dossier.IDossier': {
        'responsible': u'<G\xfcltige User-ID>',
    },
    'opengever.task.task.ITask': {
        'issuer': u'<User-ID eines g\xfcltigen Auftraggebers>',
        'responsible': u'<User-ID eines g\xfcltigen Auftragnehmers>',
        'responsible_client': u'<G\xfcltige Org-Unit-ID>',
    },
    'opengever.meeting.proposal.IProposal': {
        'issuer': u'<User-ID eines g\xfcltigen Antragsstellers>',
        'predecessor_proposal': u'<UID eines Antrags>',
        'committee_oguid': u'<OGUID eines Committees>',
        'language': u'<Ein g\xfcltiger Sprach-Code (de, en, fr...)>'
    },
    'opengever.workspace.workspace_meeting.IWorkspaceMeetingSchema': {
        'chair': u'<G\xfcltige User-ID>',
        'responsible': u'<G\xfcltige User-ID>',
        'secretary': u'<G\xfcltige User-ID>',
    },
    'opengever.workspace.workspace.IWorkspaceSchema': {
        'responsible': u'<G\xfcltige ID eines Teamraum Teilnehmers>',
    },
    'opengever.workspace.workspace_meeting_agenda_item.IWorkspaceMeetingAgendaItemSchema': {
        'related_todo_list': u'<UID einer verkn\xfcpften To-do-Liste'
    }
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
        'deadline': u'<Aktuelles Datum + 5 Tage> '
                    u':small-comment:`(konfigurierbarer Default)`',
        'responsible_client': u'<Kein Default> '
                              u':small-comment:`(Obwohl dieses Feld im User-Interface '
                              u'nicht erscheint (vom System automatisch gesetzt wird), '
                              u'muss es \xfcber die REST API angegeben werden)`',
    },
    'opengever.meeting.proposal.IProposal': {
        'language': u'<User-spezifischer Default>'
    },
    'opengever.workspace.workspace.IWorkspaceSchema': {
        'videoconferencing_url': u'<IWorkspaceSettings.videoconferencing_base_url + random UUID>',
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
    'TranslatedTextLine': {
        'type': 'string'},
    'Text': {
        'type': 'string'},
    'Tuple': {
        'type': 'array'},
    'Date': {
        'type': 'string', 'format': 'date'},
    'Datetime': {
        'type': 'string', 'format': 'datetime'},
    'UTCDatetime': {
        'type': 'string', 'format': 'datetime'},
    'Float': {
        'type': 'number'},
    'Int': {
        'type': 'integer'},
    'PropertySheetField': {
        'type': 'object'},
    'RelationList': {
        'type': 'array'},
    'RelationChoice': {
        'type': 'string'},
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
    'RichText': {
        'type': 'object'},
    'JSONField': {
        'type': 'object'},
}

PYTHON_TO_JS_TYPES = {
    int: 'integer',
    unicode: 'string',
    str: 'string',
}
