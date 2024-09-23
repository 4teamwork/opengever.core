from ftw.builder import Builder
from ftw.builder import create
from opengever.sign.utils import email_to_userid
from opengever.testing import IntegrationTestCase


class TestEmailsToUserids(IntegrationTestCase):
    def test_returns_an_empty_dict_if_no_emails_are_given(self):
        self.assertEqual('', email_to_userid(None))
        self.assertEqual('', email_to_userid(''))

    def test_properly_lookup_userid_by_email(self):
        create(Builder('ogds_user')
               .having(userid='example.user',
                       email='example@example.com'))

        self.assertEqual('', email_to_userid('unknown@example.com'))
        self.assertEqual('example.user', email_to_userid('example@example.com'))
