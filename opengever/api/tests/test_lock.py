from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestLock(IntegrationTestCase):

    @browsing
    def test_lock_is_expandable(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '?expand=lock',
                     method='GET', headers=self.api_headers)
        self.assertEqual({
            u'stealable': True, u'locked': False,
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/document-14/@lock'
        }, browser.json['@components']['lock'])
