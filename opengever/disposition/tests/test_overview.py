from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone import api


class TestDispositionOverview(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionOverview, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier A',
                                       start=date(2016, 1, 19),
                                       end=date(2016, 3, 19),
                                       public_trial='limited-public',
                                       archival_value='archival worthy'))

        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier B',
                                       start=date(2015, 1, 19),
                                       end=date(2015, 3, 19),
                                       public_trial='public',
                                       archival_value='not archival worthy',
                                       archival_value_annotation=u'In Absprache mit ARCH.'))

        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1, self.dossier2]))

    @browsing
    def test_list_only_all_disposition_dossiers(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        create(Builder('dossier').titled(u'Dossier C'))

        self.assertEquals(
            ['Client1 1 / 1 Dossier A', 'Client1 1 / 2 Dossier B'],
            browser.css('.dispositions .title').text)

    @browsing
    def test_list_details_for_each_dossiers(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        self.assertEquals(
            ['Period: Jan 19, 2016 - Mar 19, 2016',
             'Period: Jan 19, 2015 - Mar 19, 2015'],
            browser.css('.dispositions .date_period').text)

        self.assertEquals(
            ['Public Trial: limited-public', 'Public Trial: public'],
            browser.css('.dispositions .public_trial').text)

        self.assertEquals(
            ['Archival value: archival worthy ( )',
             'Archival value: not archival worthy ( In Absprache mit ARCH. )'],
            browser.css('.dispositions .archival_value').text)

    @browsing
    def test_archive_button_is_active_depending_on_the_appraisal(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        self.assertEquals(
            'Archive',
            browser.css('.appraisal-button-group .active')[0].text)

        self.assertEquals(
            "Don't archive",
            browser.css('.appraisal-button-group .active')[1].text)

    @browsing
    def test_update_appraisal_is_correct(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        self.assertEquals(
            "Archive",
            browser.css('.appraisal-button-group .active')[0].text)

        dont_archive_button = browser.css('.appraisal-button-group .button')[1]
        browser.open(dont_archive_button.get('data-url'))

        browser.login().open(self.disposition, view='tabbedview_view-overview')
        self.assertEquals(
            "Don't archive",
            browser.css('.appraisal-button-group .active')[0].text)

    @browsing
    def test_lists_possible_transitions_in_actionmenu_as_buttons(self, browser):
        self.grant('Records Manager')
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        self.assertEquals(['disposition-transition-appraise'],
                          browser.css('.transitions li').text)
        browser.css('.transitions li a').first.click()
        self.assertEquals('disposition-state-appraised',
                          api.content.get_state(self.disposition))

        browser.login().open(self.disposition, view='tabbedview_view-overview')
        self.assertEquals(['disposition-transition-dispose'],
                          browser.css('.transitions li').text)

    @browsing
    def test_sip_download_is_active_in_appraised_state(self, browser):
        self.grant('Records Manager')
        browser.login().open(self.disposition, view='tabbedview_view-overview')
        browser.find('disposition-transition-appraise').click()

        browser.open(self.disposition, view='tabbedview_view-overview')
        self.assertEquals(['Export appraisal list', 'SIP download'],
                          browser.css('ul.actions li').text)
        self.assertEquals('http://nohost/plone/disposition-1/ech0160_export',
                          browser.find('SIP download').get('href'))

    @browsing
    def test_appraisal_list_download_is_always_available(self, browser):
        self.grant('Records Manager')
        browser.login().open(self.disposition, view='tabbedview_view-overview')
        self.assertEquals(['Export appraisal list'],
                          browser.css('ul.actions li').text)
        self.assertEquals('http://nohost/plone/disposition-1/xlsx',
                          browser.find('Export appraisal list').get('href'))
