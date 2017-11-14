from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import FunctionalTestCase


class TestDispositionListing(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionListing, self).setUp()
        self.root = create(Builder('repository_root'))

    @browsing
    def test_disposition_tab_is_available_on_repositoryroots(self, browser):
        self.grant('Contributor', 'Editor', 'Reader', 'Records Manager')

        browser.login().open(self.root)

        self.assertEquals(
            ['Overview', 'Dossiers', 'Dispositions', 'Info'],
            browser.css('.tabbedview-tabs li').text)

    @browsing
    def test_disposition_tab_is_not_available_when_user_cant_add_dispositions(self, browser):
        browser.login().open(self.root)

        self.assertEquals(
            ['Overview', 'Dossiers', 'Info'],
            browser.css('.tabbedview-tabs li').text)

    @browsing
    def test_disposition_listing(self, browser):
        self.grant('Records Manager')

        with freeze(datetime(2015, 1, 1)):
            repository = create(Builder('repository').within(self.root))
            self.disposition_a = create(Builder('disposition')
                                        .titled(u'Angebot FD 23.11.2010')
                                        .within(repository))
            self.disposition_b = create(Builder('disposition')
                                        .titled(u'Angebot FD 1.2.2003')
                                        .in_state('disposition-state-appraised')
                                        .within(repository))
            self.disposition_c = create(Builder('disposition')
                                        .titled(u'Angebot FD 1.2.1995')
                                        .in_state('disposition-state-disposed')
                                        .within(repository))

        browser.login().open(self.root, view='tabbedview_view-dispositions')
        self.assertEquals(
            [{'': '',
              'Sequence Number': '1',
              'Title': 'Angebot FD 23.11.2010',
              'Review state': 'disposition-state-in-progress'},
             {'': '',
              'Sequence Number': '2',
              'Title': 'Angebot FD 1.2.2003',
              'Review state': 'disposition-state-appraised'},
             {'': '',
              'Sequence Number': '3',
              'Title': 'Angebot FD 1.2.1995',
              'Review state': 'disposition-state-disposed'}],
            browser.css('.listing').first.dicts())

    @browsing
    def test_no_tabbedview_actions_available(self, browser):
        self.grant('Records Manager')

        repository = create(Builder('repository').within(self.root))
        self.disposition_a = create(Builder('disposition').within(repository))

        browser.login().open(self.root, view='tabbedview_view-dispositions')
        self.assertEquals([''], browser.css('.tabbedview-action-list').text)

    @browsing
    def test_statefilter_hides_closed_by_default(self, browser):
        self.grant('Records Manager')

        with freeze(datetime(2015, 1, 1)):
            repository = create(Builder('repository').within(self.root))
            create(Builder('disposition')
                   .titled(u'In Progress')
                   .within(repository))
            create(Builder('disposition')
                   .titled(u'Appraised')
                   .in_state('disposition-state-appraised')
                   .within(repository))
            create(Builder('disposition')
                   .titled(u'Disposed')
                   .in_state('disposition-state-disposed')
                   .within(repository))
            create(Builder('disposition')
                   .titled(u'Disposed')
                   .in_state('disposition-state-archived')
                   .within(repository))
            create(Builder('disposition')
                   .titled(u'Closed')
                   .in_state('disposition-state-closed')
                   .within(repository))

        browser.login().open(self.root, view='tabbedview_view-dispositions')
        rows = browser.css('.listing').first.dicts()
        self.assertItemsEqual(
            ['In Progress', 'Appraised', 'Disposed', 'Disposed'],
            [row.get('Title') for row in rows])

        browser.open(self.root, view='tabbedview_view-dispositions',
                     data={'disposition_state_filter': 'filter_all'})
        rows = browser.css('.listing').first.dicts()
        self.assertItemsEqual(
            ['In Progress', 'Appraised', 'Disposed', 'Disposed', 'Closed'],
            [row.get('Title') for row in rows])
