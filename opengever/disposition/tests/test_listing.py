from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase


class TestDispositionListing(IntegrationTestCase):

    @browsing
    def test_disposition_tab_is_available_on_repositoryroots(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.repository_root)

        self.assertEquals(
            ['Overview', 'Dossiers', 'Dispositions', 'Info'],
            browser.css('.tabbedview-tabs li').text)

    @browsing
    def test_disposition_tab_is_not_available_when_user_cant_add_dispositions(self, browser):
        self.login(self.archivist, browser)
        browser.login().open(self.repository_root)

        self.assertEquals(
            ['Overview', 'Dossiers', 'Info'],
            browser.css('.tabbedview-tabs li').text)

    @browsing
    def test_disposition_listing(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2015, 1, 1)):
            self.disposition_a = create(Builder('disposition')
                                        .titled(u'Angebot FD 1.2.2003')
                                        .in_state('disposition-state-appraised')
                                        .within(self.leaf_repofolder))
            self.disposition_b = create(Builder('disposition')
                                        .titled(u'Angebot FD 1.2.1995')
                                        .in_state('disposition-state-disposed')
                                        .within(self.leaf_repofolder))

        browser.open(self.repository_root, view='tabbedview_view-dispositions')
        self.assertEquals(
            [{'': '',
              'Sequence Number': '2',
              'Title': 'Angebot FD 1.2.2003',
              'Review state': 'disposition-state-appraised'},
             {'': '',
              'Sequence Number': '3',
              'Title': 'Angebot FD 1.2.1995',
              'Review state': 'disposition-state-disposed'},
             {'': '',
              'Review state': 'disposition-state-in-progress',
              'Sequence Number': '1',
              'Title': 'Angebot 31.8.2016'}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_no_tabbedview_actions_available(self, browser):
        self.login(self.records_manager, browser)

        browser.open(self.repository_root, view='tabbedview_view-dispositions')
        self.assertEquals([''], browser.css('.tabbedview-action-list').text)

    @browsing
    def test_statefilter_hides_closed_by_default(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2015, 1, 1)):
            create(Builder('disposition')
                   .titled(u'Appraised')
                   .in_state('disposition-state-appraised')
                   .within(self.leaf_repofolder))
            create(Builder('disposition')
                   .titled(u'Disposed')
                   .in_state('disposition-state-disposed')
                   .within(self.leaf_repofolder))
            create(Builder('disposition')
                   .titled(u'Disposed')
                   .in_state('disposition-state-archived')
                   .within(self.leaf_repofolder))
            create(Builder('disposition')
                   .titled(u'Closed')
                   .in_state('disposition-state-closed')
                   .within(self.leaf_repofolder))

        self.disposition.setTitle("In Progress")
        self.disposition.reindexObject()

        browser.open(self.leaf_repofolder, view='tabbedview_view-dispositions')
        rows = browser.css('.listing').first.dicts()

        self.assertItemsEqual(
            ['In Progress', 'Appraised', 'Disposed', 'Disposed'],
            [row.get('Title') for row in rows])

        browser.open(self.leaf_repofolder, view='tabbedview_view-dispositions',
                     data={'disposition_state_filter': 'filter_all'})
        rows = browser.css('.listing').first.dicts()
        self.assertItemsEqual(
            ['In Progress', 'Appraised', 'Disposed', 'Disposed', 'Closed'],
            [row.get('Title') for row in rows])
