from opengever.base.interfaces import IReferenceNumber
from opengever.document.behaviors import IBaseDocument
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IBaseDocument, Interface)
class SerializeDocumentToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeDocumentToJson, self).__call__(*args, **kwargs)

        ref_num = IReferenceNumber(self.context)
        result[u'reference_number'] = ref_num.get_number()

        return result
