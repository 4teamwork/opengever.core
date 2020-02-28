from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import UNIT_ID_LENGTH
from opengever.setup.directives import deployment_directive
from opengever.setup.directives import ldap_directive
from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import TextLine


def register_deployment(context, **kwargs):
    title = kwargs.get('title')
    context.action(title, deployment_directive, (title, ), kw=kwargs)


class IDeploymentDirective(Interface):

    title = TextLine(
        title=u'Plone Deployment title',
        description=u'Displayed in deployment selection dropdown.',
        required=True)

    policy_profile = TextLine(
        title=u'Policy Profile',
        required=True)

    additional_profiles = Tokens(
        title=u'Additional profiles',
        description=u'Generic setup profile names (without profile- prefix)',
        default=None,
        required=True,
        value_type=TextLine()
    )

    admin_unit_id = TextLine(
        title=u'AdminUnit ID',
        description=u'AdminUnit corresponding to this plone site',
        required=True,
        max_length=UNIT_ID_LENGTH)

    mail_domain = TextLine(
        title=u'Mail domain',
        default=u'localhost',
        required=True)

    mail_from_address = TextLine(
        title=u'Mail from address',
        description=u'E-Mail address used as Plone-Site sender address',
        default=u'noreply@opengever.4teamwork.ch',
        required=True)

    is_default = Bool(
        title=u'Is Default',
        description=u'Whether this option should be pre-selected in setup.',
        default=False,
        required=True)

    reader_group = TextLine(
        title=u'Reader group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    rolemanager_group = TextLine(
        title=u'Rolemanager group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    administrator_group = TextLine(
        title=u'Administrator group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    archivist_group = TextLine(
        title=u'Archivist group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    records_manager_group = TextLine(
        title=u'Records manager group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    api_group = TextLine(
        title=u'API group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    workspace_creator_group = TextLine(
        title=u'Workspace creator group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    workspace_user_group = TextLine(
        title=u'Workspace user group',
        required=False,
        max_length=GROUP_ID_LENGTH)

    workspace_client_user_group = TextLine(
        title=u'Workspace client group',
        required=False,
        max_length=GROUP_ID_LENGTH)


def register_ldap(context, **kwargs):
    title = kwargs.get('title')
    context.action(title, ldap_directive, (title, ), kw=kwargs)


class ILDAPDirective(Interface):

    title = TextLine(
        title=u'LDAP Deployment title',
        description=u'Displayed in LDAP selection dropdown.',
        required=True)

    ldap_profile = TextLine(
        title=u'LDAP Profile',
        description=u'Profile id of the LDAP configuration profile',
        required=True)

    is_default = Bool(
        title=u'Is Default',
        description=u'Whether this option should be pre-selected in setup.',
        default=False,
        required=True)
