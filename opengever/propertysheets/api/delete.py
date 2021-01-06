from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class PropertySheetsDelete(Service):
    """
    Delete existing property sheets.

    DELETE http://localhost:8080/fd/@propertysheets/<sheet-name> HTTP/1.1
    """
    def __init__(self, context, request):
        super(PropertySheetsDelete, self).__init__(context, request)
        self.params = []
        self.storage = PropertySheetSchemaStorage()

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        if len(self.params) != 1:
            raise BadRequest(u"Missing parameter sheet_name.")

        alsoProvides(self.request, IDisableCSRFProtection)

        sheet_name = self.params.pop()
        if sheet_name not in self.storage:
            raise BadRequest(u"The property sheet '{}' does not exist.".format(sheet_name))

        self.storage.remove(sheet_name)
        self.reply_no_content()
