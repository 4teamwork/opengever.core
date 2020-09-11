from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestGroupPost(IntegrationTestCase):

    @browsing
    def test_group_creation_is_allowed_for_administrators(self, browser):
        self.login(self.workspace_owner, browser)
        payload = {
            u'groupname': u'test_group',
        }

        with browser.expect_unauthorized():
            browser.open(
                self.portal,
                view='@groups',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.login(self.administrator, browser)
        response = browser.open(
            self.portal,
            view='@groups',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/@groups/test_group',
             u'description': None,
             u'email': None,
             u'groupname': u'test_group',
             u'id': u'test_group',
             u'roles': [u'Authenticated'],
             u'title': None,
             u'users': {u'@id': u'http://nohost/plone/@groups',
                        u'items': [],
                        u'items_total': 0}},
            response.json
            )
