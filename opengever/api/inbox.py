from ftw.mail.interfaces import IEmailAddress
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.inbox.inbox import IInbox
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IInbox, Interface)
class SerializeInboxToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeInboxToJson, self).__call__(*args, **kwargs)
        result[u'email'] = IEmailAddress(self.request).get_email_for_object(
            self.context)
        return result
