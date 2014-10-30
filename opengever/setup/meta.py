from opengever.setup.directives import deployment_directive
from zope.interface import Interface
from zope.schema import TextLine


def register_deployment(_context, **kwargs):
    title = kwargs.get('title')
    _context.action(title, deployment_directive, (title, ), kw=kwargs)


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
