from opengever.dossier.behaviors.dossier import IDossierMarker
from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface


DEFAULT_DOSSIER_DEPTH = 1


class IDossierContainerTypes(Interface):
    """A type for collaborative spaces."""

    container_types = schema.List(
        title=u"container_types",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.container_types',
        ),
    )

    maximum_dossier_depth = schema.Int(
        title=u'Maximum dossier depth',
        description=u'Maximum nesting depth of dossiers and subdossiers.\
            If set to 0, no subdossiers can be created.',
        default=DEFAULT_DOSSIER_DEPTH
    )

    type_prefixes = schema.List(
        title=u"type_prefixes",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.type_prefixes',
        ),
    )


class IConstrainTypeDecider(Interface):
    """Adapter interface
    The constrain type decider decides, if a type is addable in the
    current dossier object. This decision depends on the current dossier
    type, the type to be added and the depth (distance to the next parent
    which is not an IDossier).
    Descriminators: ( request, context, FTI )
    * context : current dossier object
    * request
    * FTI: type to be added
    As Optional name the portal_type of the FTI can be used. If there is
    no such an adapter, the more general adapter without a name is used.
    """

    def __init__(self, context, request, fti):
        pass

    def addable(self, depth):
        """Returns True, if a object of type *fti* can be created in the
        current *context*, depending on the *depth*
        """
        pass


class IDossierParticipants(Interface):
    """Participants configuration (plone.registry)
    """

    roles = schema.List(
        title=u'Disabled roles of participation',
        description=u'Select the terms from the vocabulary containing the\
            possible roles of participation which should not be\
            selectable in dossiers.',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.participation_roles',
        ),
    )

    primary_participation_roles = schema.List(
        title=u'Primary participation roles',
        description=u'These roles are shown separately in the new UI',
        value_type=schema.Choice(
            vocabulary=u'opengever.dossier.participation_roles',
        ),
        required=False,
        missing_value=list(),
        default=list(),
    )


class ITemplateFolderProperties(Interface):
    """Document properties configuration.
    """

    create_doc_properties = schema.Bool(
        title=u'Enable creation of document properties',
        description=u'Select whether document properties should be created\
            when a word document is created from a document template.',
        default=False,
    )


class ITemplateDossierProperties(ITemplateFolderProperties):
    """XXX Legacy interface from rename TemplateFolder to TemplateDossier.

    Do not remove this interface until each GEVER-installation is updated to
    the version containing this change.
    """


class IParticipationCreated(IObjectEvent):
    """Interface for participation created event.
    """


class IParticipationModified(IObjectEvent):
    """Interface for participation modified event.
    """


class IParticipationRemoved(IObjectEvent):
    """Interface for participation removed event.
    """


class IDossierAttachedToEmailEvent(IObjectEvent):
    """A file from this dossier was attached to an email."""


class IDisplayedInOverviewMarker(IDossierMarker):
    """Marker Interface for additional dossier behaviors."""


class IDisplayedInOverview(Interface):
    """Super class for additional dossier behaviors."""


class IFilingNumberMaintenance(Interface):
    """Allow access to filing number internals."""

    def print_mapping():
        """Return the actual filingnumber mapping"""

    def print_filing_numbers():
        """Return a set of all filingnumbers the are used"""

    def print_filing_prefixes():
        """Reutrns all filing prefixes and their translations"""


class IDossierResolver(Interface):
    """Interface for the Dossier resolve, which provide all
    functionality needed for resolving a dossier.
    """

    def get_precondition_violations():
        """Check whether all preconditions are fulfilled.

        Return a list of errors, or an empty list when resolving is possible.
        """

    def are_enddates_valid():
        """Check if the end dates of dossiers and subdossiers are valid.
        """

    def resolve():
        """Resolve the dossier and recursly also the subdossiers.
        """


class IDossierArchiver(Interface):
    """Interface for the Dossier archiver, wich provide all the needed
    functinoality to archive a dossier (filing, filingnubmer etc.).
    """

    def generate_number(prefix, year):
        """Generate the complete filing number and
        set the number and prefix on the dossier.
        """

    def archive(prefix, year, number=None):
        """Generate a correct filing number and
        set it recursively on every subdossier.
        """

    def get_indexer_value(searchable=False):
        """Return the filing value for the filing_no indexer.
        For Dossiers without a number and only a prefix it return the half
        of the number.
        """

    def update_prefix(prefix):
        """Update the filing prefix on the dossier and
        recursively on all subdossiers.
        """


class IDossierResolveProperties(Interface):
    """Dossier resolving configuration.
    """

    purge_trash_enabled = schema.Bool(
        title=u'Enable `purge trash` option.',
        description=u'Select if the trashed documents should be deleteted '
        'when a dossier gets resolved.',
        default=False)

    journal_pdf_enabled = schema.Bool(
        title=u'Enable `journal pdf` option.',
        description=u'Select if a pdf representation of the dossier journal '
        'should be added automatically to the dossier when it gets resolved.',
        default=False)

    tasks_pdf_enabled = schema.Bool(
        title=u'Enable `tasks pdf` option.',
        description=u'Select if a pdf representation of the tasks in the dossier '
        'should be added automatically to the dossier when it gets resolved.',
        default=False)

    archival_file_conversion_enabled = schema.Bool(
        title=u'Enable automatic archival file conversion with bumblebee.',
        description=u'Select if GEVER should trigger the archival file '
        'conversion for each document, when a dossier gets resolved.',
        default=False)

    archival_file_conversion_blacklist = schema.List(
        title=u'Archival-file conversion blacklist - content types to ignore.',
        description=u'List of lowered content types for which no Archival PDF'
        ' should be generated',
        missing_value=[],
        default=[])

    resolver_name = schema.Choice(
        title=u"Dossier resolver name",
        vocabulary=u'opengever.dossier.ValidResolverNamesVocabulary',
        default='strict'
    )

    resolver_custom_precondition = schema.TextLine(
        title=u"Custom dossier resolution precondition.",
        description=u'Tales expression defining a precondition checked when '
                    u'resolving a dossier. When returning True, the dossier can '
                    u'be closed, when returning False, resolving the dossier '
                    u'will fail.',
        default=u''
    )

    resolver_custom_precondition_error_text_de = schema.TextLine(
        title=u"Error text for the resolver_custom_precondition",
        description=u'Error text displayed when the resolver_custom_precondition '
                    u'returns False.',
        default=u''
    )

    resolver_custom_after_transition_hook = schema.TextLine(
        title=u"Custom dossier resolution after transition hook.",
        description=u'Tales expression defining an after transition hook'
                    u'executing when resolving a dossier.',
        default=u''
    )

    use_changed_for_end_date = schema.Bool(
        title=u"Use the 'changed' date for earliest possible end date",
        description=u'When True, changed will be used in the calculation of '
        'the earliest possible end date. If set to False, the document_date '
        'will be used instead.',
        default=True
    )


class IDossierType(Interface):
    """plone.app.registry schema for the dossier types setting."""

    hidden_dossier_types = schema.List(
        title=u"Dossier Type",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.dossier_types',
        ),
        default=['businesscase']
    )


class IDossierChecklistSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable checklist feature',
        description=u'Whether checklist feature is enabled',
        default=False)


class IDossierSettings(Interface):

    grant_role_manager_to_responsible = schema.Bool(
        title=u'Grant Role Manager to responsible.',
        description=u'Whether the dossier responsible should be granted Role '
        'Manager role. Note that when activating this feature, Role Manager '
        'has to get assigned to the responsible on every dossier.',
        default=False)

    grant_dossier_manager_to_responsible = schema.Bool(
        title=u'Grant Dossier Manager to responsible.',
        description=u'Whether the dossier responsible should be granted Dossier '
        'Manager role. Note that when activating this feature, Dossier Manager '
        'has to get assigned to the responsible on every dossier.',
        default=False)
