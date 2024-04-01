from opengever.base.monkey.patching import MonkeyPatch
from zope.sendmail.mailer import SMTPMailer
import os


def as_bool(string):
    return string.lower() in ['1', 'yes', 'on', 'true']


class PatchMakeMailer(MonkeyPatch):
    """Patch MailHost to support configuring mail server settings through
       environment variables.
    """

    def __call__(self):

        def _makeMailer(self):
            """Create a SMTPMailer"""
            smtp_host = os.environ.get('SMTP_HOST', self.smtp_host)
            smtp_port = os.environ.get('SMTP_PORT', self.smtp_port)
            smtp_user = os.environ.get('SMTP_USER', self.smtp_uid)
            smtp_password = os.environ.get('SMTP_PASSWORD', self.smtp_pwd)
            smtp_force_tls = as_bool(os.environ.get('SMTP_FORCE_TLS', str(self.force_tls)))
            smtp_no_tls = as_bool(os.environ.get('SMTP_NO_TLS', 'False'))
            return SMTPMailer(
                hostname=smtp_host,
                port=int(smtp_port),
                username=smtp_user or None,
                password=smtp_password or None,
                no_tls=smtp_no_tls,
                force_tls=smtp_force_tls,
            )

        from Products.MailHost.MailHost import MailBase
        locals()['__patch_refs__'] = False

        self.patch_refs(MailBase, '_makeMailer', _makeMailer)
