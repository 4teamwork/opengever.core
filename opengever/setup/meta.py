from opengever.setup.directives import client_directive
from opengever.setup.directives import policy_directive
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import TextLine


def register_client(_context, **kwargs):
    _context.action(
        kwargs.get('name'),
        client_directive,
        (kwargs.get('name'), ), kw=kwargs)


def register_policy(_context, **kwargs):
    _context.action(
        kwargs.get('title'),
        policy_directive,
        (kwargs.get('title'), ), kw=kwargs)


class IClientConfiguration(Interface):

    active = Bool(
        title=u'Active Client',
        description=u'Set client as active in the ogds',
        default=False)

    local_roles = Bool(
        title=u'Set default local roles',
        default=False)

    name = TextLine(
        title=u'Client name',
        required=True)

    client_id = TextLine(
        title=u'Client ID',
        required=True)

    title = TextLine(
        title=u'Client Title',
        description=u'Client Title (for example FOO BAR)',
        required=True)

    configsql = Bool(
        title=u'configsql',
        description=u'Register the client in the OGDS clients registry.',
        default=True,
        required=False)

    ip_address = TextLine(
        title=u'IP address',
        description=u'One ore more (seperated by coma) ip-address(es), '
        'Which are used foc communcations beetwen clients.',
        required=True)

    site_url = TextLine(
        title=u'Site URL',
        description=u'Url for internal communications.',
        required=True)

    public_url = TextLine(
        title=u'Public URL',
        description=u'Public URL, accessed by the users.',
        required=True)

    group = TextLine(
        title=u'Users group',
        description=u'Groupname of the clients users group.',
        required=True)

    inbox_group = TextLine(
        title=u'Inbox group',
        description=u'Groupname of the clients inbox group.',
        required=True)

    reader_group = TextLine(
        title=u'Reader group',
        description=u'Groupname of the clients reader group.',
        required=False)

    rolemanager_group = TextLine(
        title=u'Reader group',
        description=u'Groupname of the clients reader group.',
        required=False)

    mail_domain = TextLine(
        title=u'Mail domain',
        default=u'localhost',
        required=False
    )


class IPolicyConfiguration(Interface):

    title = TextLine(
        title=u'Policy title',
        required=True)

    base_profile = TextLine(
        title=u'Base profile',
        default=u'opengever.policy.base:default',
        required=False)

    additional_profiles = TextLine(
        title=u'Additional profiles',
        description=u'Mutlitple values allowed (coma sperated list)',
        required=False)

    purge_sql = Bool(
        title=u'Drop ALL SQL tables! This option should only'
        'be used for development profiles!',
        default=False,
        required=False)

    import_users = Bool(
        title=u'Import users by default.',
        description=u'Import users after creating client.',
        default=True,
        required=False)

    language = TextLine(
        title=u'Language',
        default=u'de-ch',
        required=False)

    client_ids = TextLine(
        title=u'Ids of client configurations',
        description=u'Multiple values allowed (coma sperated list)',
        required=False)

    multi_clients = Bool(
        title=u'Policy support multiclient installations',
        required=False,
        default=False)

    repository_root_id = TextLine(
        title=u'Repository root id',
        default=u'ordnungssystem',
        required=False)

    repository_root_title = TextLine(
        title=u'Repository Root Title',
        default=u'Ordnungssystem',
        required=False)
