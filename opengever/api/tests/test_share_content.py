from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.mailer import process_mail_queue
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from plone import api
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
            'actors_to': [{'token': self.workspace_guest.getId()}],
            'actors_cc': [{'token': self.workspace_admin.getId()}],
            'comment': u'Check out this fantastic w\xf6rkspace!'
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)

        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEqual(self.workspace_guest.getProperty('email'), mail['To'])
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
            'actors_to': [{'token': self.workspace_admin.getId()},
                          {'token': self.workspace_guest.getId()}],
            'actors_cc': [{'token': self.workspace_admin.getId()},
                          {'token': self.workspace_owner.getId()}],
            'comment': u'Check out this fantastic w\xf6rkspace!'
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)
        expected_to = [self.workspace_guest.getProperty('email'),
                       self.workspace_admin.getProperty('email')]
        expected_cc = [self.workspace_owner.getProperty('email'),
                       self.workspace_admin.getProperty('email')]

        process_mail_queue()

        self.assertItemsEqual(
            expected_to + expected_cc,
            mailing.get_mailhost().messages[0].mto)

        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEqual(', '.join(expected_to), mail['To'])
        self.assertEqual(', '.join(expected_cc), mail['Cc'])
        self.assertEqual('=?utf-8?q?Schr=C3=B6dinger_B=C3=A9atrice?= <test@localhost>',
                         mail['From'])
        self.assertIn('Check out this fantastic w=C3=B6rkspace!', mail.as_string())

    @browsing
    def test_share_workspace_with_group(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        group = Group.query.get('projekt_a')
        self.set_roles(self.workspace, group.groupid, ['WorkspaceMember'])

        url = '{}/@share-content'.format(self.workspace.absolute_url())
        data = json.dumps({
            'actors_to': [{'token': 'projekt_a'}],
            'comment': u'Check out this fantastic w\xf6rkspace!'
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)
        expected_to = ', '.join((self.regular_user.getProperty('email'),
                                 self.dossier_responsible.getProperty('email')))

        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())

        self.assertEqual(expected_to, mail['To'])
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
            'actors_to': [{'token': self.workspace_guest.getId()}],
        })

        browser.open(url, method='POST', headers=self.api_headers,
                     data=data)

        process_mail_queue()
        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEqual(self.workspace_guest.getProperty('email'), mail['To'])
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
            'actors_to': [{'token': self.workspace_admin.getId()}],
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
    def test_share_content_without_actors_to_raises_bad_request(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        url = '{}/@share-content'.format(self.workspace.absolute_url())
        comment = u'Check out this fantastic w\xf6rkspace!'
        data = json.dumps({
            'actors_cc': [{'token': self.workspace_admin.getId()}],
            'comment': comment
        })

        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

        self.assertEqual(
            {"message": "Property 'notify_all' or 'actors_to' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_share_workspace_folder_notifies_all(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        browser.open(self.workspace_folder, view='@share-content', method='POST',
                     headers=self.api_headers, data=json.dumps({'notify_all': True}))

        expected_to = [self.workspace_owner.getProperty('email'),
                       self.workspace_admin.getProperty('email'),
                       self.workspace_guest.getProperty('email'),
                       self.workspace_member.getProperty('email')]

        process_mail_queue()
        self.assertItemsEqual(
            expected_to,
            mailing.get_mailhost().messages[0].mto)

        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertIsNone(mail['To'])
        self.assertIsNone(mail['Cc'])
        self.assertIsNone(mail['Bcc'])

    @browsing
    def test_share_workspace_folder_notify_all_respects_local_roles_block(self, browser):
        self.login(self.workspace_member, browser=browser)

        self.workspace_folder.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.workspace_folder).add_or_update_assignment(
            SharingRoleAssignment(api.user.get_current().getId(), ['WorkspaceMember']))

        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        browser.open(self.workspace_folder, view='@share-content', method='POST',
                     headers=self.api_headers, data=json.dumps({'notify_all': True}))

        expected_to = [self.workspace_member.getProperty('email')]

        process_mail_queue()
        self.assertItemsEqual(
            expected_to,
            mailing.get_mailhost().messages[0].mto)

        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertIsNone(mail['To'])
        self.assertIsNone(mail['Cc'])
        self.assertIsNone(mail['Bcc'])

    @browsing
    def test_share_workspace_ignores_actors_to_and_actors_cc_if_notify_all_is_set(self, browser):
        self.login(self.workspace_member, browser=browser)
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        data = json.dumps({
            'actors_to': [{'token': self.workspace_guest.getId()}],
            'actors_cc': [{'token': self.workspace_admin.getId()}],
            'comment': u'Check out this fantastic w\xf6rkspace!',
            'notify_all': True
        })

        browser.open(self.workspace_folder, view='@share-content', method='POST',
                     headers=self.api_headers, data=data)

        expected_to = [self.workspace_owner.getProperty('email'),
                       self.workspace_admin.getProperty('email'),
                       self.workspace_guest.getProperty('email'),
                       self.workspace_member.getProperty('email')]

        process_mail_queue()
        self.assertItemsEqual(
            expected_to,
            mailing.get_mailhost().messages[0].mto)

        self.assertEqual(1, len(mailing.get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertIsNone(mail['To'])
        self.assertIsNone(mail['Cc'])
        self.assertIsNone(mail['Bcc'])
        self.assertIn('Check out this fantastic w=C3=B6rkspace!', mail.as_string())

    @browsing
    def test_share_workspace_handles_missing_email_address(self, browser):
        self.login(self.workspace_member, browser=browser)
        User.query.get_by_userid(self.workspace_member.getId()).email = ""
        process_mail_queue()
        mailing = Mailing(self.portal)
        mailing.reset()

        data = json.dumps({
            'actors_to': [{'token': self.workspace_member.getId()},
                          {'token': self.workspace_guest.getId()}],
            'comment': u'Check out this fantastic w\xf6rkspace!',
        })

        browser.open(self.workspace_folder, view='@share-content', method='POST',
                     headers=self.api_headers, data=data)

        expected_to = [self.workspace_guest.getProperty('email')]

        process_mail_queue()
        self.assertItemsEqual(
            expected_to,
            mailing.get_mailhost().messages[0].mto)
