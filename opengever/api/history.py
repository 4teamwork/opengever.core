from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import getMultiAdapter


class HistoryPatch(Service):
    """ Copy of the plone.restapi.services.HistoryPatch but uses
    the ICheckinCheckoutManager to revert to an older file
    version instead of the portal_repository tool.
    """

    def reply(self):
        body = json_body(self.request)
        version = body["version"]

        # revert the file
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.revert_to_version(version)

        title = self.context.title_or_id()
        msg = u"{} has been reverted to revision {}.".format(title, version)

        return json_compatible({"message": msg})
