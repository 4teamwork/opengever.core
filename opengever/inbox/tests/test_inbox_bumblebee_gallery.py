from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase


class TestInboxBumblebeeGallery(SolrIntegrationTestCase):

    features = ('bumblebee', )

    @browsing
    def test_gallery_does_not_display_redirected_inbox_elements(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox, view='tabbedview_view-documents-gallery')
        self.assertEquals(
            [u'Dokument im Eingangsk\xf6rbli'],
            [img.attrib.get('alt') for img in browser.css('img')]
        )
