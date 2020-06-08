from datetime import datetime
from ftw.testing import freeze
from ftw.testing.mailing import Mailing
from opengever.activity.mailer import process_mail_queue
from opengever.testing import IntegrationTestCase
from opengever.workspace.invitation import valid_email
from opengever.workspace.participation import serialize_and_sign_payload
from opengever.workspace.participation.storage import IInvitationStorage
from zope.component import getUtility
import email
import unittest


class TestUnitEmailValidator(unittest.TestCase):

    def assert_valid(self, value):
        self.assertTrue(valid_email(value))

    def assert_invalid(self, value):
        self.assertFalse(valid_email(value))

    def test_invalid_email_empty(self):
        self.assert_invalid('')

    def test_invalid_email_no_at(self):
        self.assert_invalid('foobarqux.com')

    def test_invalid_email_trailing_at(self):
        self.assert_invalid('foO@')

    def test_invalid_email_leading_at(self):
        self.assert_invalid('@foO')

    def test_invalid_email_too_many_at(self):
        self.assert_invalid('foo@bar@qux')

    def test_valid_email_shortest(self):
        self.assert_valid('a@b')

    def test_valid_email_simple(self):
        self.assert_valid('email@example.com')

    def test_valid_email_firstname_lastname(self):
        self.assert_valid('firstname.lastname@example.com')

    def test_valid_email_plus(self):
        self.assert_valid('user+mailbox@example.com')


class TestInvitationMail(IntegrationTestCase):

    features = (
        'workspace',
        'activity',
        )

    def test_adding_invitation_sends_mail(self):
        self.login(self.workspace_admin)

        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()
        self.assertFalse(mailing.has_messages())

        with freeze(datetime(2019, 12, 27)):
            storage = getUtility(IInvitationStorage)
            iid = storage.add_invitation(
                self.workspace, self.regular_user.getProperty('email'),
                self.workspace_admin.getId(), 'WorkspaceGuest')
            process_mail_queue()

            self.assertTrue(mailing.has_messages())
            mails = mailing.get_messages()
            self.assertEqual(1, len(mails))
            mail = email.message_from_string(mails[0])

            self.assertIn('test@localhost', mail.get("From"))
            self.assertEqual(self.regular_user.getProperty('email'), mail.get("To"))

            payload = {"iid": iid}
            payload = serialize_and_sign_payload(payload)

        link = "{}/@@my-invitations/accept?invitation={}".format(self.workspace.absolute_url(), payload)
        self.assertIn(link, mail.as_string().decode('quoted-printable'))
