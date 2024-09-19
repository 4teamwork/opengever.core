from ftw.solr.interfaces import ISolrDocument
from Products.ZCatalog.interfaces import ICatalogBrain
from zope import schema
from zope.component import getAdapters
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import json


class IOpengeverBaseLayer(Interface):
    """Marker interfaces for opengever base browserview customisations.
    """


class IDuringContentCreation(Interface):
    """Request layer to indicate that content is currently being created.
    """


class IInternalWorkflowTransition(Interface):
    """Request layer to indicate workflow transitions triggered by
    other actions.
    """


class IDontIssueDossierReferenceNumber(Interface):
    """Request layer to indicate that no reference number should be issued
    when creating new dossiers.
    """


class INoSeparateConnectionForSequenceNumbers(Interface):
    """Request layer to indicate no separate ZODB connection should be used
    to issue sequence numbers.
    """


class IOpengeverCatalogBrain(ICatalogBrain):
    """Detailed Interface for opengever CatalogBrain.
    Used for add an opengever specific CatalogContentlisting Adapter.
    """


class IBaseCustodyPeriods(Interface):
    custody_periods = schema.List(title=u"custody period",
                                  default=[u'0',
                                           u'30',
                                           u'100',
                                           u'150',
                                           ],
                                  value_type=schema.TextLine(),
                                  )


class IRetentionPeriodRegister(Interface):
    """ plone.registry register for retention_period
    """
    retention_period = schema.List(
        title=u'Retention period',
        description=u'Possible values for retention period in years.',
        default=[u'5',
                 u'10',
                 u'15',
                 u'20',
                 u'25'],
        value_type=schema.TextLine(),)


class IReferenceNumberPrefix(Interface):
    """ The Reference Number Prefix Adapter Interface """


class IReferenceNumber(Interface):
    """ The reference number adapter is able to generate a full reference
    number including all parent reference-prefixes.
    Examples:

    GD 2.3 / 4.5 / 123
    * GD : client specific short name
    * 2 : reference_number prefix of first RepositoryFolder
    * 3 : reference_number prefix of second RepositoryFolder
    * / : Seperator between RFs and Dossiers
    * 4 : reference_number prefix of first dossier
    * 5 : reference_number prefix of second dossier
    * / : Seperator between Dossiers and Document
    * 123 : sequence_number of Document
    """

    def get_number():
        """ Returns the reference number of the context
        """

    def get_sortable_number(self):
        """ Returns the sortable reference number of the context
        """

    def get_local_number():
        """Returns only the reference number part of the context."""

    def add_local_number(numbers):
        """Adds the number part of the context in the specific list
        in the passed numbers dict."""

    def get_numbers():
        """Returns a dict of lists of all number parts, from the context up to
        the plone site, grouped by the context type.

        Examples:
        {'site': ['OG'],
         'repository: ['3', '5' , '8']',
         'dossier: ['3', '3']'}
        """


class IReferenceNumberFormatter(Interface):

    def complete_number(numbers):
        """Generate the complete reference number, for the given numbers dict.
        """

    def complete_sortable_number(numbers):
        """Generate a sortable version of the complete reference number,
        for the given numbers dict.
        """

    def repository_number(numbers):
        """Generate the reposiotry reference number part,
        for the given numbers dict.
        """

    def dossier_number(numbers):
        """Generate the dossier reference number part,
        for the given numbers dict.
        """

    def sorter(brain_or_value):
        """Sort-key function that knows how to sort complete reference
        numbers produced by this formatter.
        """


@implementer(IVocabularyFactory)
class ReferenceFormatterVocabulary(object):
    """ Vocabulary of all users with a valid login.
    """

    def __call__(self, context):
        terms = []

        for name, formatter in getAdapters(
                [context, ], IReferenceNumberFormatter):
            terms.append(SimpleTerm(name))
        return SimpleVocabulary(terms)


DEFAULT_FORMATTER = 'dotted'
DEFAULT_PREFIX_STARTING_POINT = u'1'


class IReferenceNumberSettings(Interface):

    formatter = schema.Choice(
        title=u'Reference number formatter',
        description=u'Select one of the registered'
        'IReferenceNumberFormatter adapter',
        source='opengever.base.ReferenceFormatterVocabulary',
        default=DEFAULT_FORMATTER)

    reference_prefix_starting_point = schema.TextLine(
        title=u"Starting Point for reference_number prefixs",
        description=u"Used as default when creating the first item on a level.",
        default=DEFAULT_PREFIX_STARTING_POINT)


class ISequenceNumber(Interface):
    """  The sequence number utility provides a getNumber(obj) method
    which returns a unique number for each object.
    """

    def get_number(self, obj):
        """ Returns the sequence number for the given *obj*
        """


class ISequenceNumberGenerator(Interface):
    """ The sequence number generator adapter generates a new sequence number
    for the adapted object
    """

    def generate(self):
        """ Returns a new sequence number for the adapted object
        """


class IRedirector(Interface):
    """An adapter for the BrowserRequest to redirect a user after loading the
    next page to a specific URL which is opened in another window / tab with
    the name "target".
    """

    def redirect(url, target='_blank'):
        """Redirects the user to a `url` which is opened in a window called
        `target` after loading the next page.
        """

    def get_redirects(remove=True):
        """Returns a list of dicts containing the redirect informations. If
        `remove` is set to `True` (default) the redirect infos are deleted.
        """


class IUniqueNumberUtility(Interface):
    """The unique number utility provides the a dynamic counter functionality,
    for the given object and keyword-arguments.
    It generates a unique key for every keywoards and values combination,
    including the portal_type except the keyword 'portal_type' is given.
    For every key he provide the get_number and remove_number functioniality.
    """

    def get_number(self, obj, **keys):
        """Return the stored value for the combinated key, if no entry exists,
        it generates one with the help of the unique number generator.
        """

    def remove_number(self, obj, **keys):
        """Remove the entry in the local storage for the combinated key.
        """


class IUniqueNumberGenerator(Interface):
    """The unique nuber generator adapter, handle for every key a counter with
    the highest assigned value. So he provides the generate functionality,
    which return the next number, for every counter.
    """

    def generate(self, key):
        """Return the next number for the given key.
        """


class IRepositoryPathSourceBinderQueryModificator(Interface):
    """Markerinterface for RepositoryPathSourceBinderQueryModificator
    adapter"""

    def modify_query(self, query):
        """Modify the ReppositoryPathSourceBinderQuery"""


class IDataCollector(Interface):
    """Interface for adapters which are able to serialize and
    deserialize data. With these named-adapters any kind of additional
    information can be transmitted.
    Discriminators: object
    Name: unique adapter name, which is used as key for sending the data
    """

    def extract(self):
        """Returns the serialized data. Serialized data consists of raw
        type data (dicts, lists, tuples, strings, numbers, bools, etc. ).
        The data is json-able.
        """

    def insert(self, data):
        """Deserializes the *data* and changes the *obj* according to the
        data.
        """


class IGeverState(Interface):
    """A view that provides traversable helper methods to be used in templates
    or TAL expressions, similar to Plone's portal_state view.
    """

    def cluster_base_url():
        """Base URL of the GEVER cluster (includes trailing slash).
        """

    def gever_portal_url():
        """URL of the GEVER portal.
        """

    def cas_server_url():
        """URL of the CAS server.
        """

    def is_readonly():
        """Whether this instance is in readonly mode.
        """

    def properties_action_available():
        """Check if properties action is available.
        """


class IGeverSettings(Interface):
    """Provide the current site configuration."""

    def get_config():
        """Provide a nested OrderedDict of the current site configuration."""


class ISQLObjectWrapper(Interface):
    """Marker interface for sql object wrappers."""


class ISQLFormSupport(Interface):
    """Provides helper methods for sql forms.
    """

    def is_editable(self):
        """Defines if the form is editable or not.

        returns: bool
        """

    def get_edit_url(self, context):
        """Returns the url to the edit-view of the model.
        """

    def get_edit_values(self, fieldnames):
        """Returns the a dict with filednames and values of the given fieldnames.

        Filednames which are not provided by the model will be skipped.
        """

    def update_model(self, data):
        """Updated the model-fields given in data-dict.
        """


class IOGSolrDocument(ISolrDocument):
    """OpenGever Solr Document"""


class IBaseSettings(Interface):

    is_redis_error_log_feature_enabled = schema.Bool(
        title=u'Enable Redis error logging feature',
        description=u'Makes backend errors accessible for users',
        default=False)

    possible_watcher_groups_white_list_regex = schema.TextLine(
        title=u'white list regex for possible watcher groups',
        description=u'Regex pattern for groups which should be allowed as'
        'possible watchers',
        default=u"^.+")


class ISearchSettings(Interface):

    use_solr = schema.Bool(
        title=u'Use Solr',
        description=u'Enables Solr for search forms.',
        default=True,
    )


class IFavoritesSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable favorites feature',
        description=u'Whether favorite feature is enabled',
        default=True)


class IRecentlyTouchedSettings(Interface):

    limit = schema.Int(
        title=u'Max number of recently touched objs to store and display',
        description=u'How many entries to keep for a users recently touched '
                    u'items list.',
        default=10)


class IOGMailSettings(Interface):

    send_with_actor_from_address = schema.Bool(
        title=u"Send mails with actor's email address in From: header",
        description=u"Whether mails sent on behalf of actors (users) should "
                    u"be sent with the user's email address in the From: "
                    u"header. The default (False) is to use the system's "
                    u"'noreply' address instead (to avoid sender address "
                    u"spoofing).",
        default=False)


DEFAULT_DASHBOARD_CARDS = [
    {
        'id': 'newest_gever_notifications',
        'componentName': 'NewestGeverNotificationsCard'
    },
    {
        'id': 'recently_touched_items',
        'componentName': 'RecentlyTouchedItemsCard'
    },
    {
        'id': 'my_dossiers',
        'title_de': 'Meine Dossiers',
        'title_en': 'My dossiers',
        'title_fr': 'Mes dossiers',
        'componentName': 'DossiersCard',
        'responsibleToggleFilters': ['myDossiers', 'anyParticipation'],
    },
    {
        'id': 'substitute_dossiers',
        'componentName': 'SubstituteDossiersCard'
    },
    {
        'id': 'dashboard_pending_tasks',
        'componentName': 'DashboardPendingTasksCard'
    },
    {
        'id': 'substitute_tasks',
        'componentName': 'SubstituteTasksCard'
    },
    {
        'id': 'dashboard_all_pending_tasks',
        'componentName': 'DashboardAllPendingTasksCard'
    },
    {
        'id': 'my_proposals',
        'componentName': 'MyProposalsCard',
        'listingKey': 'proposals',
        'pivotKey': 'issuer-current-user'
    },
    {
        'id': 'my_watched_tasks',
        'componentName': 'MyWatchedTasksCard',
        'listingKey': 'tasks',
        'pivotKey': 'watcher-current-user'},
    {
        'id': 'my_watched_documents',
        'componentName': 'MyWatchedDocumentsCard',
        'listingKey': 'documents',
        'pivotKey': 'watcher-current-user'
    }]


class IGeverUI(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable new GEVER UI',
        description=u'Whether new GEVER UI is enabled',
        default=True)

    is_classic_ui_enabled = schema.Bool(
        title=u'Enable the classic UI',
        default=True)

    custom_dashboard_cards = schema.Text(
        title=u'custom dashboard cards',
        description=u'In json format, eg. [{"id": "dossiers", "componentName": "DossiersCard", "'
        'title_de": "Falldossiers", "filters": { "dossierType": "Falldossier"'
        ' }}]',
        default=json.dumps(DEFAULT_DASHBOARD_CARDS).decode('utf-8'))


class IHubSpotSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable HubSpot',
        description=u'Whether HubSpot is enabled',
        default=False)


class IUserSnapSettings(Interface):
    """XXX: Not used anymore, can be deleted once
    20220510174043_remove_user_snap_settings has been executed for all deployments
    """
    api_key = schema.TextLine(
        title=u"API key",
        description=u"API key for the usersnap widget.",
        default=u"")


class IDocPropertyProvider(Interface):
    """A provider for DocProperties."""

    def get_properties(prefix=None):
        """Return a dictionary of DocProperties.

        All keys will be prefixed by the default application prefix, followed
        by the optional prefix argument.
        """


class ITeasersSettings(Interface):

    show_teasers = schema.Bool(
        title=u'Show teasers',
        description=u'Whether the teasers should be shown',
        default=True)

    teasers_to_hide = schema.List(title=u"Teasers to hide",
                                  default=[],
                                  value_type=schema.TextLine(),
                                  )


class IRoleAssignmentReportsStorage(Interface):
    """Storage abstraction for role assignment reports.
    """

    def initialize_storage():
        """If not present already, initialize internal storage data structures.
        """

    def add(principal_id):
        """Add a role assignment report for the given principal_id.
        """

    def get(report_uid):
        """Return the corresponding role assignment report.
        """

    def update(report_uid, report_data):
        """Update the corresponding role assignment report.
        """

    def list():
        """List all role assignment reports in storage.
        """

    def delete(report_uid):
        """Delete the corresponding role assignment report.
        """


class IMovabilityChecker(Interface):

    def validate_movement(target):
        """Raises an error if object cannot be moved.
        """


class IPortalSettings(Interface):

    portal_url = schema.TextLine(
        title=u'Portal url',
        description=u'This url will be exposed in the @config endpoint and will '
                    u'be used to generate the workspace invitation url. '
                    u'Leave it blank to use an auto generated portal url to '
                    u'[cluster-base-url]/portal')


class IWhiteLabelingSettings(Interface):

    color_scheme_light = schema.TextLine(
        title=u'Color scheme light',
        description=u'In json format, eg. {"primary":"#55ff00"}', default=u'{}')

    dossier_type_colors = schema.TextLine(
        title=u'Dossier type color',
        description=u'In json format, eg. {"businesscase":"#55ff00"}', default=u'{}')

    show_created_by = schema.Bool(
        title=u'Show created by section',
        description=u'Whether created by section should be shown',
        default=True)

    custom_support_markup_de = schema.Text(title=u'Custom support markup de', required=False)

    custom_support_markup_en = schema.Text(title=u'Custom support markup en', required=False)

    custom_support_markup_fr = schema.Text(title=u'Custom support markup fr', required=False)

    logo_src = schema.Bytes(title=u'Logo image',
                            description=u'Format must be png, height must be 30px')


AVATAR_SOURCE_PLONE_ONLY = 'plone_only'
AVATAR_SOURCE_PORTAL_ONLY = 'portal_only'
AVATAR_SOURCE_AUTO = 'auto'


def get_user_avatar_image_sources():
    return SimpleVocabulary.fromValues([
        AVATAR_SOURCE_PLONE_ONLY,
        AVATAR_SOURCE_PORTAL_ONLY,
        AVATAR_SOURCE_AUTO,
    ])


class IActorSettings(Interface):

    user_avatar_image_source = schema.Choice(
        title=u"User avatar image source",
        source=get_user_avatar_image_sources(),
        default=AVATAR_SOURCE_PLONE_ONLY,
    )


class IListingActions(Interface):
    """Adapter to determine listing actions"""

    def get_actions():
        """Return listing actions"""


class IContextActions(Interface):
    """Adapter to determine context actions"""

    def get_actions():
        """Return context actions"""


class IDeleter(Interface):
    """Interface for the Deleter adapter.
    """

    def delete():
        """ Deletes the adapted context if possible.

        This method should do permission checks and validate all necessary preconditions.
        """

    def verify_may_delete():
        """Performs all security checks and validates all preconditions.

        This function should raise a Forbidden-error if any validation fails.
        """

    def is_delete_allowed():
        """Returns a boolean, indicating if the context could be deleted.
        """


class IConfigCheckManager(Interface):
    def check_all():
        """It returns a list of all configuration errors if something is not
        properly configured.

        The list will be empty if there are no errors
        """


class IConfigCheck(Interface):
    def check():
        """Runs the specific check.

        It returns a dict with error metadata for missconfigurated configs
        """
