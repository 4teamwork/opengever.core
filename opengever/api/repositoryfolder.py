from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.base.interfaces import IReferenceNumber
from opengever.repository.interfaces import IRepositoryFolder
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IRepositoryFolder, Interface)
class SerializeRepositoryFolderToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeRepositoryFolderToJson, self).__call__(*args, **kwargs)

        result[u'is_leafnode'] = self.context.is_leaf_node()

        ref_num = IReferenceNumber(self.context)
        result[u'reference_number'] = ref_num.get_number()

        return result
