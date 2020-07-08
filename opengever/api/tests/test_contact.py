from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestContactGet(IntegrationTestCase):

    @browsing
    def test_contact_get(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.franz_meier, headers=self.api_headers)

        self.assertDictContainsSubset({
                u'@id': u'http://nohost/plone/kontakte/meier-franz',
                u'@type': u'opengever.contact.contact',
                u'review_state': u'contact-state-active',
                u'email': u'meier.f@example.com',
                u'id': u'meier-franz',
                u'relative_path': u'kontakte/meier-franz',
                u'review_state': u'contact-state-active',
                u'firstname': u'Franz',
                u'lastname': u'Meier',
            },
            browser.json
        )
