from five import grok
from plone.app.workflow import PloneMessageFactory as _
from plone.app.workflow import permissions
from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implements


class AdministratorRole(grok.GlobalUtility):
    grok.name('Administrator')
    implements(ISharingPageRole)

    title = _(u"title_can_administrate", default=u"Can administrate")
    required_permission = permissions.DelegateRoles


class PublisherRole(grok.GlobalUtility):
    grok.name('Publisher')
    implements(ISharingPageRole)

    title = _(u"title_can_publish", default=u"Can publish")
    required_permission = permissions.DelegateRoles
