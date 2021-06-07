from ftw.mail.inbound import MailInbound
from opengever.mail.exceptions import MessageContainsVirus
from opengever.virusscan.validator import validateUploadForFieldIfNecessary
from six import BytesIO
from zope.interface import Invalid


class GeverMailInbound(MailInbound):

    def msg(self):
        """We add scanning for viruses and raise an exception inheriting from
        MailInboundException, setting an appropriate exit code.
        """
        msg = super(GeverMailInbound, self).msg()
        filelike = BytesIO(msg)
        filename = '<stream>'

        try:
            validateUploadForFieldIfNecessary(
                'message', filename, filelike, self.request)
        except Invalid as e:
            raise MessageContainsVirus(e.message)
        return msg
