from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.meeting.model import Period
from opengever.testing import IntegrationTestCase
import os


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
            date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31),
            committee=self.committee.load_model()))
        create(Builder('period').having(
            title=u'2011',
            date_from=date(2011, 1, 1),
            date_to=date(2011, 12, 31),
            committee=self.committee.load_model()))

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
            title=u'Foo', date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31), committee=self.committee.load_model()))
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

        period = self.committee.load_model().periods[0]
        expected_url = os.path.join(
            period.get_url(self.committee), 'alphabetical_toc/as_json')
        self.assertEqual(expected_url, button.get("href"))

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

        period = self.committee.load_model().periods[0]
        expected_url = os.path.join(period.get_url(self.committee), 'repository_toc/as_json')
        self.assertEqual(expected_url, button.get("href"))

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

        period = self.committee.load_model().periods[0]
        expected_url = os.path.join(period.get_url(self.committee), 'dossier_refnum_toc/as_json')
        self.assertEqual(expected_url, button.get("href"))

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

        period = self.committee.load_model().periods[0]
        expected_url = os.path.join(period.get_url(self.committee), 'repository_refnum_toc/as_json')
        self.assertEqual(expected_url, button.get("href"))

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
