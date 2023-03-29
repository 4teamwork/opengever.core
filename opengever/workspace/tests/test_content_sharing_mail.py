from ftw.testing.mailing import Mailing
from opengever.activity.mailer import process_mail_queue
from opengever.testing import IntegrationTestCase
from opengever.workspace.content_sharing_mailer import ContentSharingMailer
import email


class TestContentSharingMail(IntegrationTestCase):
    features = ('workspace', 'activity')

    def test_content_sharing_mail(self):
        self.login(self.workspace_member)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        mailer = ContentSharingMailer()
        sender_id = self.workspace_member.getId()
        emails_to = self.workspace_owner.getProperty('email')
        emails_cc = self.workspace_admin.getProperty('email')
        emails_bcc = self.workspace_guest.getProperty('email')
        comment = u'Check out this interesting w\xf6rkspace!'
        mailer.share_content(self.workspace, sender_id, emails_to, emails_cc, emails_bcc, comment)
        process_mail_queue()
        message = Mailing(self.portal).get_mailhost().messages.pop()
        mail = email.message_from_string(message.messageText)

        self.assertItemsEqual([emails_to, emails_cc, emails_bcc], message.mto)
        self.assertEqual(emails_to, mail['To'])
        self.assertEqual(emails_cc, mail['Cc'])
        self.assertEqual('=?utf-8?q?Schr=C3=B6dinger_B=C3=A9atrice?= <test@localhost>',
                         mail['From'])
        self.assertIn('Check out this interesting w=C3=B6rkspace!', mail.as_string())
