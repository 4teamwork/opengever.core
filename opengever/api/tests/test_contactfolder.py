from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestContactFolderGet(IntegrationTestCase):

    @browsing
    def test_contactfolder_get(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.contactfolder, headers=self.api_headers)

        self.assertDictContainsSubset({
                u'@id': u'http://nohost/plone/kontakte',
                u'@type': u'opengever.contact.contactfolder',
                u'review_state': u'contactfolder-state-active',
                u'id': u'kontakte',
                u'relative_path': u'kontakte',
                u'title_de': u'Kontakte',
                u'title_fr': None,
            },
            browser.json
        )
