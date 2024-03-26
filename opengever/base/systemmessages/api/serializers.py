from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.model import get_locale
from opengever.base.systemmessages.models import SystemMessage
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(SystemMessage, IOpengeverBaseLayer)
class SerializeSystemMessagesToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    content_type = 'virtual.ogds.systemmessage'

    def __call__(self):
        sys_msg = self.context
        result = json_compatible({
            'id': sys_msg.id,
            'admin_unit': sys_msg.admin_unit_id,
            'text_en': sys_msg.text_en,
            'text_de': sys_msg.text_de,
            'text_fr': sys_msg.text_fr,
            'start_ts': sys_msg.start_ts,
            'end_ts': sys_msg.end_ts,
            'type': sys_msg.type,
        })

        url = '/'.join((
            api.portal.get().absolute_url(),
            '@system-messages/%s' % sys_msg.id,
        ))
        result.update({'@id': url})
        result.update({'@type': self.content_type})
        result.update({'text': self.get_text_field(sys_msg)})
        result.update(({'active': sys_msg.is_active()}))

        return result

    def get_current_lang(self):
        return get_locale()

    def get_text_field(self, sys_msg):
        """Get the appropriate text field based on the preferred language."""
        preferred_language = self.get_current_lang()
        text_field = None

        # Try preferred language first
        if preferred_language == 'de' and sys_msg.text_de:
            text_field = sys_msg.text_de
        elif preferred_language == 'en' and sys_msg.text_en:
            text_field = sys_msg.text_en
        elif preferred_language == 'fr' and sys_msg.text_fr:
            text_field = sys_msg.text_fr

        # If no translation found in preferred language, try fallback languages
        if not text_field:
            if sys_msg.text_de:
                text_field = sys_msg.text_de
                return text_field
            elif sys_msg.text_fr:
                text_field = sys_msg.text_fr
                return text_field
            else:
                return sys_msg.text_en
        return text_field
