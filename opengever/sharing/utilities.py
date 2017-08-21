from plone.app.workflow import permissions
from plone.app.workflow import PloneMessageFactory as _
from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implementer


@implementer(ISharingPageRole)
class AdministratorRole(object):
    title = _(u"title_can_administrate", default=u"Can administrate")
    required_permission = permissions.DelegateRoles


@implementer(ISharingPageRole)
class PublisherRole(object):
    title = _(u"title_can_publish", default=u"Can publish")
    required_permission = permissions.DelegateRoles
