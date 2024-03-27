from opengever.base.model import create_session
from opengever.base.systemmessages.api.base import SystemMessageLocator


class SystemMessagesDelete(SystemMessageLocator):
    """API Endpoint that deletes a SystemMessage.

    DELETE /@system-messages/19 HTTP/1.1
    """

    def reply(self):
        sys_msg = self.locate_message()
        session = create_session()
        session.delete(sys_msg)
        return self.reply_no_content()
