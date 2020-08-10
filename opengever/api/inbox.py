from ftw.mail.interfaces import IEmailAddress
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.utils import get_current_org_unit
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

        # org_unit does not have to be configured on an inbox. If it isn't
        # we default to the current org_unit.
        orgunit = self.context.get_responsible_org_unit() or get_current_org_unit()
        result[u'inbox_id'] = orgunit.inbox().id()
        return result
