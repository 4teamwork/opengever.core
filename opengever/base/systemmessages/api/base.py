from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


class SystemMessagesBase(Service):
    """Base service class for all @system-messages endpoints.
    """

    def render(self):
        return super(SystemMessagesBase, self).render()

    def serialize(self, sys_msg):
        return getMultiAdapter((sys_msg, getRequest()), ISerializeToJson)()
