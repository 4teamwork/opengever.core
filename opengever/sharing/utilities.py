from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.workflow import permissions
from Products.CMFCore import permissions as core_permissions
from five import grok

from plone.app.workflow import PloneMessageFactory as _


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