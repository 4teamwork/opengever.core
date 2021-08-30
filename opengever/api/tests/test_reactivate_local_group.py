from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName
import json


class TestReactivateLocalGroupPost(IntegrationTestCase):

    @browsing
    def test_reactivate_local_group(self, browser):
        self.groupid = u'test_group'
        group_users = [ogds_service().find_user(user.getId())
                       for user in [self.workspace_member, self.workspace_guest]]
        ogds_group = create(Builder('ogds_group').having(groupid=self.groupid, active=False,
                                                         is_local=True, users=group_users))
        payload = {
            u'groupname': self.groupid,
        }

        self.login(self.administrator, browser)

        browser.open(
            self.portal,
            view='@reactivate-local-group',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertTrue(ogds_group.active)
        plone_group = getToolByName(self.portal, "portal_groups").getGroupById(self.groupid)
        self.assertIsNotNone(plone_group)
        self.assertEqual({self.workspace_member.getId(), self.workspace_guest.getId()},
                         set(plone_group.getGroupMemberIds()))

    @browsing
    def test_group_reactivation_is_allowed_for_administrators(self, browser):
        self.groupid = u'test_group'
        create(Builder('ogds_group').having(groupid=self.groupid, active=False, is_local=True))

        self.login(self.workspace_owner, browser)
        portal_groups = getToolByName(self.portal, "portal_groups")
        self.assertIsNone(portal_groups.getGroupById(self.groupid))

        payload = {
            u'groupname': self.groupid,
        }

        with browser.expect_unauthorized():
            browser.open(
                self.portal,
                view='@reactivate-local-group',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertIsNone(portal_groups.getGroupById(self.groupid))

        self.login(self.administrator, browser)
        browser.open(
            self.portal,
            view='@reactivate-local-group',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

    @browsing
    def test_cannot_reactivate_active_group(self, browser):
        self.login(self.administrator, browser)

        payload = {
            u'groupname': u'committee_rpk_group',
        }

        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@reactivate-local-group',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'], u'Can only reactivate inactive groups.')
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_can_not_reactivate_global_group(self, browser):
        self.groupid = u'test_group'
        create(Builder('ogds_group').having(groupid=self.groupid, active=False, is_local=False))
        self.login(self.administrator, browser)

        payload = {
            u'groupname': self.groupid,
        }

        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@reactivate-local-group',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'], u'Can only reactivate local groups.')
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_group_reactivation_fails_if_groupname_is_missing(self, browser):
        self.login(self.administrator, browser)

        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@reactivate-local-group',
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'], "Property 'groupname' is required.")
        self.assertEqual(browser.json[u'type'], u'BadRequest')

    @browsing
    def test_group_reactivation_fails_if_groupname_is_invalid(self, browser):
        self.login(self.manager, browser)

        payload = {
            u'groupname': u'invalid',
        }
        with browser.expect_http_error(400):
            browser.open(
                self.portal,
                view='@reactivate-local-group',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(
            browser.json[u'message'],
            u'Group invalid does not exist in OGDS.')
        self.assertEqual(browser.json[u'type'], u'BadRequest')
