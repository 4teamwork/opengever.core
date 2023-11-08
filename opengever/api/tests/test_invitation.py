from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from opengever.workspace.exceptions import DuplicatePendingInvitation
from opengever.workspace.exceptions import MultipleUsersFound
from opengever.workspace.participation import WORKSPCAE_GUEST
from opengever.workspace.participation.storage import IInvitationStorage
from zope.component import getUtility
import json


def get_entry_by_token(entries, token):
    for entry in entries:
        if entry['token'] == token:
            return entry
    return None


class TestInvitationsPost(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_adding_new_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)

        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': self.regular_user.getProperty('email'),
            'role': {'token': WORKSPCAE_GUEST.id},
        })

        with freeze(datetime(2016, 12, 9, 9, 40)):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

        item = browser.json
        iid = item.get('token')
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/workspaces/workspace-1/@invitations/{}'.format(iid),
                u'@type': u'virtual.participations.invitation',
                u'inviter_fullname': u'Hugentobler Fridolin (fridolin.hugentobler)',
                u'recipient_email': u'foo@example.com',
                u'role': {
                    'token': 'WorkspaceGuest',
                    'title': 'Guest',
                },
                u'token': iid,
            },
            item)

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertDictEqual(
            item,
            get_entry_by_token(browser.json.get('items'), iid),
            "The serialized invitation from the POST request should be the "
            "same as the serialized invitation in the GET request.")

    @browsing
    def test_endpoint_ignores_unknown_properties(self, browser):
        self.login(self.workspace_admin, browser=browser)

        url = '{}/@invitations'.format(self.workspace.absolute_url())

        # The `@type` property is not defined in the IWorkspaceInvitationSchema.
        # The endpoint should not fail if this property is present.
        data = json.dumps({
            '@type': 'virtual.participation.invitation',
            'recipient_email': self.regular_user.getProperty('email'),
            'role': {'token': WORKSPCAE_GUEST.id},
        })
        browser.open(url, method='POST', headers=self.api_headers, data=data)
        item = browser.json
        iid = item.get('token')
        self.assertEqual(
            u'http://nohost/plone/workspaces/workspace-1/@invitations/{}'.format(iid),
            item['@id'])

    @browsing
    def test_prevents_duplicate_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)

        storage = getUtility(IInvitationStorage)
        storage.add_invitation(self.workspace,
                               u'foo@example.com',
                               self.workspace_admin.getId(),
                               WORKSPCAE_GUEST.id)

        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': u'foo@example.com',
            'role': {'token': WORKSPCAE_GUEST.id},
        })

        with self.assertRaises(DuplicatePendingInvitation):
            browser.exception_bubbling = True
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

    @browsing
    def test_raises_when_multiple_users_have_same_email(self, browser):
        fa_users = ogds_service().fetch_group('fa_users')

        create(Builder('ogds_user')
                .id('foo.bar')
                .having(
                    firstname='foo',
                    lastname='bar',
                    email='twice@example.com',
                )
                .in_group(fa_users))

        create(Builder('ogds_user')
                .id('bar.qux')
                .having(
                    firstname='bar',
                    lastname='qux',
                    email='twice@example.com',
                )
                .in_group(fa_users))

        ogds_service().session.flush()

        self.login(self.workspace_admin, browser=browser)

        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': u'twice@example.com',
            'role': {'token': WORKSPCAE_GUEST.id},
        })

        with self.assertRaises(MultipleUsersFound):
            browser.exception_bubbling = True
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

    @browsing
    def test_prevents_invalid_emails(self, browser):
        self.login(self.workspace_admin, browser=browser)

        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': u'f@',
            'role': {'token': WORKSPCAE_GUEST.id},
        })

        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

    @browsing
    def test_can_only_add_workspace_related_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)
        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': u'foo@example.com',
            'role': {'token': 'Reader'},
        })

        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

        data = json.dumps({
            'recipient_email': u'foo@example.com',
            'role': {'token': 'Site Administrator'},
        })

        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

    @browsing
    def test_member_cannot_use_post_endpoint(self, browser):
        self.login(self.workspace_member, browser=browser)

        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': self.regular_user.getProperty('email'),
            'role': {'token': 'WorkspaceAdmin'},
        })

        with browser.expect_http_error(401):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)

    @browsing
    def test_guest_cannot_use_post_endpoint(self, browser):
        self.login(self.workspace_guest, browser=browser)

        url = '{}/@invitations'.format(self.workspace.absolute_url())
        data = json.dumps({
            'recipient_email': self.regular_user.getProperty('email'),
            'role': {'token': 'WorkspaceAdmin'},
        })

        with browser.expect_http_error(401):
            browser.open(url, method='POST', headers=self.api_headers,
                         data=data)


class TestInvitationsDelete(IntegrationTestCase):

    @browsing
    def test_delete_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)
        storage = getUtility(IInvitationStorage)
        iid = storage.add_invitation(
            self.workspace,
            self.regular_user.getProperty('email'),
            self.workspace_admin.getId(),
            'WorkspaceGuest')

        browser.open(
            self.workspace.absolute_url() + '/@invitations',
            method='GET',
            headers=self.api_headers,
        )

        self.assertIsNotNone(
            get_entry_by_token(browser.json.get('items'), iid),
            'Expect an invitation.')

        browser.open(
            self.workspace.absolute_url() + '/@invitations/{}'.format(iid),
            method='DELETE',
            headers=self.api_headers,
        )

        self.assertEqual(204, browser.status_code)

        browser.open(
            self.workspace.absolute_url() + '/@invitations',
            method='GET',
            headers=self.api_headers,
        )

        self.assertIsNone(
            get_entry_by_token(browser.json.get('items'), iid),
            'Expect no invitation anymore.')
