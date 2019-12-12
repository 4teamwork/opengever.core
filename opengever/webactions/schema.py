from opengever.api.validation import Base64DataURI
from zope.interface import Interface
from zope.interface import invariant
from zope.interface.exceptions import Invalid
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Int
from zope.schema import List
from zope.schema import TextLine
from zope.schema import URI


GEVER_TYPES = [
    'opengever.dossier.businesscasedossier',
    'opengever.document.document',
    'ftw.mail.mail',
    'opengever.contact.contact',
    'opengever.repository.repositoryfolder',
    'opengever.repository.repositoryroot',
]

ACTION_PERMISSIONS = [
    'edit',
    'trash',
    'untrash',
    'manage-security',
] + ['add:%s' % pt for pt in GEVER_TYPES]


ICON_PROPERTIES = ['icon_name', 'icon_data']


class IWebActionSchema(Interface):
    """Schema to describe WebActions.

    This is used by the storage as well as the REST API to validate
    dictionaries or PersistentMappings when adding webactions, or updating
    existing ones.
    """

    title = TextLine(
        title=u'Title',
        description=u'Title of the webaction',
        required=True)

    unique_name = TextLine(
        title=u'Unique Name',
        description=u'Unique, client-controlled label',
        required=False)

    target_url = URI(
        title=u'Target URL',
        description=u'Target URL of the 3rd party application',
        required=True)

    enabled = Bool(
        title=u'Enabled',
        description=u'Whether this webaction is enabled or not',
        required=False,
        missing_value=True)

    icon_name = ASCIILine(
        title=u'Icon Name',
        description=u'Name of a "Font Awesome" icon for this webaction',
        required=False)

    icon_data = Base64DataURI(
        title=u'Icon Data URI',
        description=u'A complete data URI (Base64 encoded) with the icon for this webaction',
        required=False)

    display = Choice(
        title=u'Display Location',
        description=u'Where in the UI the webaction should be displayed.',
        values=[
            'action-buttons',
            'actions-menu',
            'add-menu',
            'title-buttons',
            'user-menu',
        ],
        required=True)

    mode = Choice(
        title=u'Mode',
        description=u'How the target_url will be opened',
        values=[
            'self',
            'blank',
            # TODO: 'modal'
        ],
        required=True)

    order = Int(
        title=u'Order',
        description=u'Ordering hint [0-100] (0 means first, 100 means last)',
        min=0,
        max=100,
        required=True)

    scope = Choice(
        title=u'Scope',
        description=u'Where the webaction applies.',
        values=[
            'global',
            # TODO: 'context' (needs more discussion)
            # TODO: 'recursive'
        ],
        required=True)

    types = List(
        title=u'Types',
        description=u'On which portal_types the webaction should be available',
        # These should possibly be made dynamic at some point.
        # Maybe factor out some of the definitions from
        # opengever.base.schemadump.config into vocabularies?
        value_type=Choice(values=GEVER_TYPES),
        required=False,
        missing_value=list())

    groups = List(
        title=u'Groups',
        description=u'List of groups this action is to be shown for. The '
                    u'action is only shown when the user is in at least one '
                    u'of these groups, as determined by querying the OGDS.',
        value_type=TextLine(),
        required=False)

    permissions = List(
        title=u'Permissions',
        description=u'List of permissions this action makes sense for. The '
                    u'action is only shown when the user has at least one '
                    u'of those permissions on the respective context.',
        value_type=Choice(values=ACTION_PERMISSIONS),
        required=False,
        missing_value=list())

    comment = TextLine(
        title=u'Comment',
        description=u'Comment for this webaction',
        required=False)

    @invariant
    def icon_present_for_display_types_that_need_it(self):
        display = self.display
        has_icon = any(getattr(self, key, None) not in ('', None) for key in (ICON_PROPERTIES))

        icon_required = ('title-buttons', 'add-menu')
        icon_forbidden = ('actions-menu', 'user-menu')
        icon_optional = ('action-buttons', )  # noqa

        if display in icon_forbidden:
            if has_icon:
                raise Invalid("Display location %r doesn't allow an icon." % display)

        elif display in icon_required:
            if not has_icon:
                raise Invalid('Display location %r requires an icon.' % display)

    @invariant
    def no_more_than_one_icon(self):
        icons = filter(None, (getattr(self, key, None) for key in (ICON_PROPERTIES)))
        if len(icons) > 1:
            raise Invalid(
                'Icon properties %r are mutually exclusive. '
                'At most one icon allowed.' % ICON_PROPERTIES)


class IWebActionMetadataSchema(Interface):
    """Metadata fields automatically added by the server.
    """

    action_id = Int(
        title=u'Action ID',
        description=u'Automatically assigned unique ID for this action',
        required=True)

    created = Datetime(
        title=u'Created',
        description=u'Time when this action was created.',
        required=True)

    modified = Datetime(
        title=u'Modified',
        description=u'Time when this action was last modified.',
        required=True)

    owner = TextLine(
        title=u'Owner',
        description=u'User that created the action.',
        required=True)


class IPersistedWebActionSchema(IWebActionSchema, IWebActionMetadataSchema):
    """The full schema of a persisted webaction, including metadata fields
    added by the server, not just the user-controlled fields.
    """
