from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from lxml.cssselect import CSSSelector
from opengever.base.security import elevated_privileges
from opengever.disposition.interfaces import IHistoryStorage
from opengever.latex.listing import ILaTexListing
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import getMultiAdapter
import lxml


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
              'Review state': 'disposition-state-appraised',
              'Sequence Number': '3',
              'Title': 'Angebot FD 1.2.2003'},
             {'': '',
              'Review state': 'disposition-state-disposed',
              'Sequence Number': '4',
              'Title': 'Angebot FD 1.2.1995'},
             {'': '',
              'Review state': 'disposition-state-in-progress',
              'Sequence Number': '1',
              'Title': 'Angebot 31.8.2016'},
             {'': '',
              'Review state': 'disposition-state-disposed',
              'Sequence Number': '2',
              'Title': 'Angebot 30.12.1997'}],
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

        self.disposition_with_sip.setTitle("Disposed")
        self.disposition_with_sip.reindexObject()

        browser.open(self.leaf_repofolder, view='tabbedview_view-dispositions')
        rows = browser.css('.listing').first.dicts()

        self.assertItemsEqual(
            ['In Progress', 'Appraised', 'Disposed', 'Disposed', 'Disposed'],
            [row.get('Title') for row in rows])

        browser.open(self.leaf_repofolder, view='tabbedview_view-dispositions',
                     data={'disposition_state_filter': 'filter_all'})
        rows = browser.css('.listing').first.dicts()
        self.assertItemsEqual(
            ['In Progress', 'Appraised', 'Disposed', 'Disposed', 'Disposed', 'Closed'],
            [row.get('Title') for row in rows])


class BaseLatexListingTest(IntegrationTestCase):

    def assert_row_values(self, expected, row):
        self.assertEquals(
            expected,
            [value.text_content().strip() for value in
             row.xpath(CSSSelector('td').path)])

    def get_listing_rows(self, obj, listing_name, items):
        listing = getMultiAdapter(
            (obj, obj.REQUEST, self),
            ILaTexListing, name=listing_name)
        listing.items = items

        table = lxml.html.fromstring(listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)
        return rows


class TestDestroyedDossierListing(BaseLatexListingTest):

    def test_listing(self):
        self.login(self.regular_user)
        with elevated_privileges():
            api.content.transition(obj=self.disposition, transition='disposition-transition-appraise')
            api.content.transition(obj=self.disposition, transition='disposition-transition-dispose')
            api.content.transition(obj=self.disposition, transition='disposition-transition-archive')
            api.content.transition(obj=self.disposition, transition='disposition-transition-close')

        rows = self.get_listing_rows(self.disposition,
                                     'destroyed_dossiers',
                                     self.disposition.get_dossier_representations())

        self.assert_row_values(
            ['Client1 1.1 / 12', 'Hannah Baufrau', 'Yes'], rows[0])
        self.assert_row_values(
            ['Client1 1.1 / 14', 'Hans Baumann', 'No'], rows[1])


class TestDispositionHistoryListing(BaseLatexListingTest):

    def test_listing(self):
        self.login(self.records_manager)

        with freeze(datetime(2016, 11, 1, 11, 0)):
            storage = IHistoryStorage(self.disposition)
            storage.add('edited', api.user.get_current().getId(), [])

        with freeze(datetime(2016, 11, 6, 12, 33)), elevated_privileges():
            api.content.transition(self.disposition,
                                   'disposition-transition-appraise')
            api.content.transition(self.disposition,
                                   'disposition-transition-dispose')

        with freeze(datetime(2016, 11, 16, 8, 12)), elevated_privileges():
            api.content.transition(self.disposition,
                                   'disposition-transition-archive')

        rows = self.get_listing_rows(self.disposition,
                                     'disposition_history',
                                     self.disposition.get_history())

        expected_rows = [
            ['Nov 16, 2016 08:12 AM', 'Flucht Ramon (ramon.flucht)', 'disposition-transition-archive'],
            ['Nov 06, 2016 12:33 PM', 'Flucht Ramon (ramon.flucht)', 'disposition-transition-dispose'],
            ['Nov 06, 2016 12:33 PM', 'Flucht Ramon (ramon.flucht)', 'disposition-transition-appraise'],
            ['Nov 01, 2016 11:00 AM', 'Flucht Ramon (ramon.flucht)', 'Disposition edited'],
            ['Aug 31, 2016 07:07 PM', 'Flucht Ramon (ramon.flucht)', 'Disposition added']]

        for row, expected_row in zip(rows, expected_rows):
            self.assert_row_values(expected_row, row)

    def test_transition_label_for_added_and_edited_entries_is_translated_correctly(self):
        self.login(self.records_manager)

        storage = IHistoryStorage(self.disposition)
        storage.add('edited', api.user.get_current().getId(), [])

        rows = self.get_listing_rows(self.disposition,
                                     'disposition_history',
                                     self.disposition.get_history())

        self.assert_row_values(
            ['Disposition edited'], rows[0][2])
        self.assert_row_values(
            ['Disposition added'], rows[1][2])
