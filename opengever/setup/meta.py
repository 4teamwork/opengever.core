from opengever.setup.directives import deployment_directive
from opengever.setup.directives import ldap_directive
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

    base_profile = TextLine(
        title=u'Base Profile',
        default=u'opengever.policy.base:default',
        required=True)

    policy_profile = TextLine(
        title=u'Policy Profile',
        required=True)

    additional_profiles = TextLine(
        title=u'Additional profiles',
        description=u'Multiple values allowed (coma sperated)',
        required=False)

    admin_unit_id = TextLine(
        title=u'AdminUnit ID',
        description=u'AdminUnit corresponding to this plone site',
        required=True)

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
        required=False)

    rolemanager_group = TextLine(
        title=u'Rolemanager group',
        required=False)

    administrator_group = TextLine(
        title=u'Administrator group',
        required=False)


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
