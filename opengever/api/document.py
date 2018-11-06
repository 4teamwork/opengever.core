from opengever.base.interfaces import IReferenceNumber
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import ICheckinCheckoutManager
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from opengever.api.serializer import GeverSerializeToJson
from plone.restapi.services.content.update import ContentPatch
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IBaseDocument, Interface)
class SerializeDocumentToJson(GeverSerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeDocumentToJson, self).__call__(*args, **kwargs)

        ref_num = IReferenceNumber(self.context)
        result[u'reference_number'] = ref_num.get_number()

        return result


class DocumentPatch(ContentPatch):

    def reply(self):

        # Only allow updating a documents file if the document is checked-out
        # by the current user.
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        if not manager.is_checked_out_by_current_user():
            data = json_body(self.request)
            if 'file' in data:
                self.request.response.setStatus(403)
                return dict(error=dict(
                    type='Forbidden',
                    message='Document not checked-out by current user.'))

        return super(DocumentPatch, self).reply()
