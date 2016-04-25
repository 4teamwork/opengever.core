from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDispositionListing(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionListing, self).setUp()
        self.root = create(Builder('repository_root'))

    @browsing
    def test_disposition_tab_is_available_on_repositoryroots(self, browser):
        browser.login().open(self.root)

        self.assertEquals(
            ['overview', 'dossiers', 'dispositions', 'sharing'],
            browser.css('.tabbedview-tabs li').text)

    @browsing
    def test_disposition_listing(self, browser):
        repository = create(Builder('repository').within(self.root))
        self.disposition_a = create(Builder('disposition').within(repository))
        self.disposition_b = create(Builder('disposition').within(repository))
        self.disposition_c = create(Builder('disposition').within(repository))

        browser.login().open(self.root, view='tabbedview_view-dispositions')
        self.assertEquals(
            [{'':'', 'Sequence Number': '1', 'Title': 'Disposition 1'},
             {'':'', 'Sequence Number': '2', 'Title': 'Disposition 2'},
             {'':'', 'Sequence Number': '3', 'Title': 'Disposition 3'}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_no_tabbedview_actions_available(self, browser):
        repository = create(Builder('repository').within(self.root))
        self.disposition_a = create(Builder('disposition').within(repository))

        browser.login().open(self.root, view='tabbedview_view-dispositions')
        self.assertEquals([''], browser.css('.tabbedview-action-list').text)
