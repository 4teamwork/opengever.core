from opengever.base.interfaces import IOpengeverBaseLayer
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter


@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverSerializeToJson(SerializeToJson):
    """
    """


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class GeverSerializeFolderToJson(SerializeFolderToJson):
    """
    """
