from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.systemmessages.models import SystemMessages
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(SystemMessages, IOpengeverBaseLayer)
class SerializeSystemMessagesToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    content_type = 'virtual.ogds.systemmessages'

    def __call__(self):
        sys_msg = self.context
        result = json_compatible({
            'id': sys_msg.id,
            'admin_unit': sys_msg.admin_unit_id,
            'text_en': sys_msg.text_en,
            'text_de': sys_msg.text_de,
            'text_fr': sys_msg.text_fr,
            'start': sys_msg.start,
            'end': sys_msg.end,
            'type': sys_msg.type,
        })

        url = '/'.join((
            api.portal.get().absolute_url(),
            '@system-messages/%s' % sys_msg.id,
        ))
        result.update({'@id': url})
        result.update({'@type': self.content_type})
        return result
