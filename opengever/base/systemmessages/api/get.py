from opengever.base.systemmessages.api.base import SystemMessageLocator
from plone import api


class SystemMessagesGet(SystemMessageLocator):
    """API Endpoint that returns systemMessages.

    GET /@system-messages/1 HTTP/1.1
    GET /@system-messages HTTP/1.1
    """

    def reply(self):
        if self.msg_id:
            # Get message by id
            msg = self.locate_message()
            return self.serialize(msg)

        # List all system messages
        return self.list()

    def list(self):
        msgs = self.list_messages()
        result = {
            '@id': '/'.join((api.portal.get().absolute_url(), '@system-messages')),
            'items': [self.serialize(msg) for msg in msgs],
        }
        return result
