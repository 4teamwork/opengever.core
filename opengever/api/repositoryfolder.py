from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix as PrefixAdapter
from opengever.repository.interfaces import IRepositoryFolder
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import BadRequest
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IDeserializeFromJson)
@adapter(IRepositoryFolder, Interface)
class DeserializeRepositoryFolderFromJson(DeserializeFromJson):

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        number = data.get('reference_number_prefix')
        if number:
            self.validate_reference_number(number, create=create)

        return super(DeserializeRepositoryFolderFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)

    def validate_reference_number(self, number, create=False):
        parent = aq_parent(aq_inner(self.context))
        if create:
            is_valid = PrefixAdapter(parent).is_valid_number(number)
        else:
            is_valid = PrefixAdapter(parent).is_valid_number(number,
                                                             self.context)
        if not is_valid:
            msg = "The reference_number {} is already in use.".format(number)
            error = {
                "message": msg,
                "field": "reference_number",
                "error": "ValidationError"
            }
            raise BadRequest([error])


@implementer(ISerializeToJson)
@adapter(IRepositoryFolder, Interface)
class SerializeRepositoryFolderToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeRepositoryFolderToJson, self).__call__(*args, **kwargs)

        result[u'is_leafnode'] = self.context.is_leaf_node()

        ref_num = IReferenceNumber(self.context)
        result[u'reference_number'] = ref_num.get_number()

        return result
