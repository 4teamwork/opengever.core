from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.meeting.exceptions import MultiplePeriodsFound
from opengever.meeting.period import Period
from opengever.testing import IntegrationTestCase
import os
import pytz


class TestPathBar(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_committee_member_cant_see_period_edit_links(self, browser):
        self.login(self.meeting_user, browser)

        browser.open(self.committee, view='tabbedview_view-periods')
        listing = browser.css('#period_listing').first
        self.assertEqual(
            '2016 (Jan 01, 2016 - Dec 31, 2016) '
            'download TOC alphabetical '
            'download TOC by repository '
            'download TOC by dossier reference number '
            'download TOC by repository reference number',
            listing.text
            )


class TestPeriod(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_periods_tab(self, browser):
        self.login(self.committee_responsible, browser)

        create(Builder('period').having(
            title=u'2010',
            start=date(2010, 1, 1),
            end=date(2010, 12, 31)).within(self.committee))
        create(Builder('period').having(
            title=u'2011',
            start=date(2011, 1, 1),
            end=date(2011, 12, 31)).within(self.committee))

        browser.open(self.committee, view='tabbedview_view-periods')
        period_rows = browser.css('#period_listing .period')
        text_by_period = [row.css('> *').text for row in period_rows]
        self.assertEqual([
            ['2016 (Jan 01, 2016 - Dec 31, 2016)',
             'download TOC alphabetical download TOC by repository '
             'download TOC by dossier reference number download TOC by repository reference number',
             'Edit'],
            ['2011 (Jan 01, 2011 - Dec 31, 2011)',
             'download TOC alphabetical download TOC by repository '
             'download TOC by dossier reference number download TOC by repository reference number',
             'Edit'],
            ['2010 (Jan 01, 2010 - Dec 31, 2010)',
             'download TOC alphabetical download TOC by repository '
             'download TOC by dossier reference number download TOC by repository reference number',
             'Edit']
        ], text_by_period)

    @browsing
    def test_edit_period(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-periods')
        browser.find('Edit').click()
        browser.fill({'Start date': '20.01.2016'}).submit()

        self.assertEqual(['Changes saved'], info_messages())
        self.assertEqual(date(2016, 1, 20), self.period.start)

    @browsing
    def test_close_and_create_new_period_new(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.committee)
        browser.find('Close current period').click()

        browser.fill({'Title': u'Old',
                      'Start date': '01.01.2012',
                      'End date': '31.12.2012'}).submit()
        browser.fill({'Title': u'New',
                      'Start date': '01.01.2013',
                      'End date': '31.12.2013'}).submit()

        self.assertEqual(["Record created"], info_messages())

        committee_model = browser.context.load_model()  # refresh model
        self.assertEqual(2, len(committee_model.periods))
        old_period = committee_model.periods[0]
        new_period = committee_model.periods[1]

        self.assertEqual('closed', old_period.workflow_state)
        self.assertEqual(u'Old', old_period.title)
        self.assertEqual(date(2012, 1, 1), old_period.date_from)
        self.assertEqual(date(2012, 12, 31), old_period.date_to)
        self.assertEqual('active', new_period.workflow_state)
        self.assertEqual(u'New', new_period.title)
        self.assertEqual(date(2013, 1, 1), new_period.date_from)
        self.assertEqual(date(2013, 12, 31), new_period.date_to)

    def test_period_title_with_start_and_end_date(self):
        self.login(self.meeting_user)
        period = create(Builder('period').having(
            title=u'Foo', start=date(2010, 1, 1), end=date(2010, 12, 31))
            .within(self.committee))
        self.assertEqual('Foo (Jan 01, 2010 - Dec 31, 2010)',
                         period.get_title())

    @browsing
    def test_toc_json_button_only_shown_for_managers(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.committee, view='tabbedview_view-periods')
        period_rows = browser.css('#period_listing .period')
        text_by_period = [row.css('> *').text for row in period_rows]
        self.assertEqual([
            ['2016 (Jan 01, 2016 - Dec 31, 2016)',
             'download TOC alphabetical download TOC by repository '
             'download TOC by dossier reference number download TOC by repository reference number',
             'Edit'],
        ], text_by_period)

        self.login(self.manager, browser)
        browser.open(self.committee, view='tabbedview_view-periods')
        period_rows = browser.css('#period_listing .period')
        text_by_period = [row.css('> *').text for row in period_rows]
        self.assertEqual([
            ['2016 (Jan 01, 2016 - Dec 31, 2016)',
             'download TOC alphabetical download TOC by repository '
             'download TOC by dossier reference number download TOC by repository reference number',
             'Edit',
             'download TOC json alphabetical download TOC json repository '
             'download TOC json by dossier reference number download TOC json by repository reference number'],
        ], text_by_period)

    @browsing
    def test_toc_json_alphabetical_button(self, browser):
        self.login(self.manager, browser)

        browser.open(self.committee, view='tabbedview_view-periods')
        button = browser.find('download TOC json alphabetical')

        button.click()
        toc_content = {u'toc': [{u'group_title': u'I',
                                 u'contents': [{u'decision_number': 1,
                                                u'dossier_reference_number': u'Client1 1.1 / 1',
                                                u'has_proposal': True,
                                                u'meeting_date': u'17.07.2016',
                                                u'meeting_start_page_number': None,
                                                u'repository_folder_title': u'Vertr\xe4ge und Vereinbarungen',
                                                u'title': u'Initialvertrag f\xfcr Bearbeitung',
                                                u'description': None}],
                                 }]}
        self.assertEqual(toc_content, browser.json)

    @browsing
    def test_toc_json_repository_button(self, browser):
        self.login(self.manager, browser)
        browser.open(self.committee, view='tabbedview_view-periods')
        button = browser.find('download TOC json repository')

        button.click()
        toc_content = {u'toc': [{u'group_title': u'Vertr\xe4ge und Vereinbarungen',
                                 u'contents': [{u'decision_number': 1,
                                                u'dossier_reference_number': u'Client1 1.1 / 1',
                                                u'has_proposal': True,
                                                u'meeting_date': u'17.07.2016',
                                                u'meeting_start_page_number': None,
                                                u'repository_folder_title': u'Vertr\xe4ge und Vereinbarungen',
                                                u'title': u'Initialvertrag f\xfcr Bearbeitung',
                                                u'description': None}],
                                 }]}

        self.assertEqual(toc_content, browser.json)

    @browsing
    def test_toc_json_dossier_reference_number_button(self, browser):
        self.login(self.manager, browser)
        browser.open(self.committee, view='tabbedview_view-periods')
        button = browser.find('download TOC json by dossier reference number')

        button.click()
        toc_content = {u'toc': [{u'group_title': u'Client1 1.1 / 1',
                                 u'contents': [{u'decision_number': 1,
                                                u'description': None,
                                                u'dossier_reference_number': u'Client1 1.1 / 1',
                                                u'has_proposal': True,
                                                u'meeting_date': u'17.07.2016',
                                                u'meeting_start_page_number': None,
                                                u'repository_folder_title': u'Vertr\xe4ge und Vereinbarungen',
                                                u'title': u'Initialvertrag f\xfcr Bearbeitung'}],
                                 }]}

        self.assertEqual(toc_content, browser.json)

    @browsing
    def test_toc_json_repository_reference_number_button(self, browser):
        self.login(self.manager, browser)

        browser.open(self.committee, view='tabbedview_view-periods')
        button = browser.find('download TOC json by repository reference number')

        button.click()
        toc_content = {u'toc': [{u'group_title': u'Client1 1.1',
                                 u'contents': [{u'decision_number': 1,
                                                u'description': None,
                                                u'dossier_reference_number': u'Client1 1.1 / 1',
                                                u'has_proposal': True,
                                                u'meeting_date': u'17.07.2016',
                                                u'meeting_start_page_number': None,
                                                u'repository_folder_title': u'Vertr\xe4ge und Vereinbarungen',
                                                u'title': u'Initialvertrag f\xfcr Bearbeitung'}],
                                 }]}

        self.assertEqual(toc_content, browser.json)


class TestGetCurrentPeriod(IntegrationTestCase):

    features = ('meeting',)

    def test_returns_period_for_current_date_by_default(self):
        self.login(self.committee_responsible)
        with freeze(datetime(2016, 10, 16, 0, 0, tzinfo=pytz.utc)):
            self.assertEqual(self.period, Period.get_current(self.committee))

    def test_return_period_for_contained_date(self):
        self.login(self.committee_responsible)
        self.assertEqual(
            self.period, Period.get_current(self.committee, date(2016, 3, 9)))

    def test_return_period_first_date_of_range(self):
        self.login(self.committee_responsible)
        self.assertEqual(
            self.period, Period.get_current(self.committee, date(2016, 1, 1)))

    def test_return_period_last_date_of_range(self):
        self.login(self.committee_responsible)
        self.assertEqual(
            self.period, Period.get_current(self.committee, date(2016, 12, 31)))

    def test_returns_none_when_date_before_period_range(self):
        self.login(self.committee_responsible)
        self.assertIsNone(Period.get_current(self.committee, date(2013, 1, 1)))

    def test_returns_none_when_date_after_period_range(self):
        self.login(self.committee_responsible)
        self.assertIsNone(Period.get_current(self.committee, date(2017, 1, 1)))

    def test_raises_when_multiple_periods_found(self):
        self.login(self.committee_responsible)
        create(Builder('period').having(
            title=u'duplicate 2016',
            start=date(2016, 3, 1),
            end=date(2016, 7, 1)).within(self.committee))

        with self.assertRaises(MultiplePeriodsFound):
            Period.get_current(self.committee, date(2016, 5, 1))

    def test_unrestricted_search_returns_all_periods(self):
        with self.login(self.committee_responsible):
            committee = self.committee
            period = self.period

        self.assertEqual(
            period, Period.get_current(committee, date(2016, 12, 31),
                                       unrestricted=True))
