from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base.interfaces import IOpengeverBaseLayer
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter


def extend_with_bumblebee_checksum(result, context):
    if IBumblebeeable.providedBy(context):
        result['bumblebee_checksum'] = IBumblebeeDocument(context).get_checksum()


@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverSerializeToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeToJson, self).__call__(*args, **kwargs)

        extend_with_bumblebee_checksum(result, self.context)

        return result


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class GeverSerializeFolderToJson(SerializeFolderToJson):
    """
    """
