from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.mailer import process_mail_queue
from opengever.testing import IntegrationTestCase
import email
import json


class TestShareContentPost(IntegrationTestCase):
    features = ('workspace', 'activity')

    @browsing
    def test_share_workspace(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        url = '{}/@share-content'.format(self.workspace.absolute_url())
        data = json.dumps({
            'users_to': [{'token': self.archivist.getId()}],
            'users_cc': [{'token': self.workspace_admin.getId()}],
            'comment': u'Check out this fantastic w\xf6rkspace!'
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)

        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEqual(self.archivist.getProperty('email'), mail['To'])
        self.assertEqual(self.workspace_admin.getProperty('email'), mail['Cc'])
        self.assertEqual('=?utf-8?q?Schr=C3=B6dinger_B=C3=A9atrice?= <test@localhost>',
                         mail['From'])
        self.assertIn('Check out this fantastic w=C3=B6rkspace!', mail.as_string())

    @browsing
    def test_share_workspace_folder_with_multiple_recipients(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        url = '{}/@share-content'.format(self.workspace_folder.absolute_url())
        data = json.dumps({
            'users_to': [{'token': self.archivist.getId()},
                         {'token': self.workspace_guest.getId()}],
            'users_cc': [{'token': self.workspace_admin.getId()},
                         {'token': self.workspace_owner.getId()}],
            'comment': u'Check out this fantastic w\xf6rkspace!'
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)
        expected_to = ', '.join((self.archivist.getProperty('email'),
                                 self.workspace_guest.getProperty('email')))
        expected_cc = ', '.join((self.workspace_admin.getProperty('email'),
                                 self.workspace_owner.getProperty('email')))

        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEqual(expected_to, mail['To'])
        self.assertEqual(expected_cc, mail['Cc'])
        self.assertEqual('=?utf-8?q?Schr=C3=B6dinger_B=C3=A9atrice?= <test@localhost>',
                         mail['From'])
        self.assertIn('Check out this fantastic w=C3=B6rkspace!', mail.as_string())

    @browsing
    def test_share_todo_without_cc_recipients_and_comment(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        url = '{}/@share-content'.format(self.workspace.absolute_url())
        data = json.dumps({
            'users_to': [{'token': self.archivist.getId()}],
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)

        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEqual(self.archivist.getProperty('email'), mail['To'])
        self.assertIsNone(mail.get('Cc'))
        self.assertEqual('=?utf-8?q?Schr=C3=B6dinger_B=C3=A9atrice?= <test@localhost>',
                         mail['From'])

    @browsing
    def test_share_document_outside_a_workspace_raises_bad_request(self, browser):
        self.login(self.workspace_member, browser=browser)
        doc_in_workspace = create(Builder('document').within(self.workspace))
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        url = '{}/@share-content'.format(doc_in_workspace.absolute_url())
        data = json.dumps({
            'users_to': [{'token': self.workspace_admin.getId()}],
        })
        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)
        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))

        url = '{}/@share-content'.format(self.document.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

        self.assertEqual(
            {"message": "'{}' is not within a workspace".format(self.document.getId()),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_share_content_without_users_to_raises_bad_request(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        url = '{}/@share-content'.format(self.workspace.absolute_url())
        comment = u'Check out this fantastic w\xf6rkspace!'
        data = json.dumps({
            'users_cc': [{'token': self.workspace_admin.getId()}],
            'comment': comment
        })

        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

        self.assertEqual(
            {"message": "Property 'users_to' is required",
             "type": "BadRequest"},
            browser.json)
