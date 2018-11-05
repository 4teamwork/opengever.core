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

    def is_resolve_possible():
        """Check if all preconditions are fulfilled.
        """

    def are_enddates_valid():
        """Check if the end dates of dossiers and subdossiers are valid.
        """

    def is_archive_form_needed():
        """Check if the archive form must be rendered or not."""

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


class IDocProperties(Interface):
    """Adapts IDossierMarker.
    """

    def get_properties():
        """Return a dictionary of DocProperties for the adapted dossier.
        """


class IDocPropertyProvider(Interface):
    """May adapt any object that can be a provider for DocProperties.
    """

    def get_properties():
        """Return a dictionary of DocProperties for the adapted object.
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

    resolver_name = schema.Choice(
        title=u"Dossier resolver name",
        vocabulary=u'opengever.dossier.ValidResolverNamesVocabulary',
        default='strict'
    )


"""
These two interfaces have been moved and renamed to
opengever.document.interfaces.IDossierTasksPDFMarker and
opengever.document.interfaces.IDossierJournalPDFMarker
Once leftovers have been cleaned up with upgrade step
opengever/core/upgrades/20181101074702_add_automatically_generated_document_interface
they can be deleted here (the upgrade step too)
"""


class IDossierTasksPdfMarker(Interface):
    """Depraceted marker Interface for dossier tasks list document."""


class IDossierJournalPdfMarker(Interface):
    """Deprecated marker Interface for dossier journal document."""
