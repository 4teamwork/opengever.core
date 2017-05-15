from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestDispositionOverview(FunctionalTestCase):
    """Test disposition overviews function as intended."""

    def setUp(self):
        super(TestDispositionOverview, self).setUp()
        self.grant('Records Manager')
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .titled(u'Repository A')
                                 .having(
                                     archival_value=ARCHIVAL_VALUE_SAMPLING)
                                 .within(self.root))
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
                               .in_state('dossier-state-inactive')
                               .within(self.repository)
                               .having(title=u'Dossier B',
                                       start=date(2015, 1, 19),
                                       end=date(2015, 3, 19),
                                       public_trial='public',
                                       archival_value='not archival worthy',
                                       archival_value_annotation=u''
                                       u'In Absprache mit ARCH.'))

        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[
                                      self.dossier1,
                                      self.dossier2,
                                      ]))

    @browsing
    def test_list_only_all_disposition_dossiers(self, browser):
        browser.login().open(self.disposition, view='overview')

        create(Builder('dossier').titled(u'Dossier C'))

        self.assertEquals(
            ['Client1 1 / 1 Dossier A', 'Client1 1 / 2 Dossier B'],
            browser.css('.dispositions .title').text)

    @browsing
    def test_list_details_for_each_dossiers(self, browser):
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            ['Period: Jan 19, 2016 - Mar 19, 2016',
             'Period: Jan 19, 2015 - Mar 19, 2015'],
            browser.css('.dispositions .date_period').text)

        self.assertEquals(
            ['Public Trial: limited-public', 'Public Trial: public'],
            browser.css('.dispositions .public_trial').text)

        self.assertEquals(
            ['Archival value: archival worthy',
             'Archival value: not archival worthy ( In Absprache mit ARCH. )'],
            browser.css('.dispositions .archival_value').text)

    @browsing
    def test_archive_button_is_active_depending_on_the_appraisal(self, browser):  # noqa
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            'Archive',
            browser.css('.appraisal-button-group .active')[0].get('title'))
        self.assertEquals(
            "Don't archive",
            browser.css('.appraisal-button-group .active')[1].get('title'))

    @browsing
    def test_appraisal_buttons_are_only_links_in_progress_state(self, browser):
        self.grant('Archivist')
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            ['Archive', "Don't archive"],
            [link.get('title') for link
             in browser.css('.appraisal-button-group').first.css('a')])
        browser.find('disposition-transition-appraise').click()

        browser.login().open(self.disposition, view='overview')
        self.assertEquals(
            [],
            [link.get('title') for link
             in browser.css('.appraisal-button-group').first.css('a')])

        buttons = browser.css('.appraisal-button-group')
        self.assertEquals(['Archive'],
                          [link.get('title') for link
                           in buttons[0].css('span')])
        self.assertEquals(["Don't archive"],
                          [link.get('title') for link
                           in buttons[1].css('span')])

    @browsing
    def test_update_appraisal_displays_buttons_correctly(self, browser):
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            ['Archive', "Don't archive"],
            [link.get('title') for link
             in browser.css('.appraisal-button-group .active')])

        button = browser.css('.appraisal-button-group .archive')[1]
        url = browser.css('#disposition_overview').first.get(
            'data-appraisal_update_url')
        data = {'dossier-id': button.get('data-intid'),
                'should_be_archived': button.get('data-archive')}
        browser.open(url, data)

        browser.open(self.disposition, view='overview')
        self.assertEquals(
            ['Archive', 'Archive'],
            [link.get('title') for link
             in browser.css('.appraisal-button-group .active')])

    @browsing
    def test_lists_possible_transitions_in_actionmenu_as_buttons(self, browser):  # noqa
        self.grant('Archivist', 'Records Manager')
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(['disposition-transition-appraise',
                           'disposition-transition-refuse'],
                          browser.css('.transitions li').text)
        browser.css('.transitions li a').first.click()
        self.assertEquals('disposition-state-appraised',
                          api.content.get_state(self.disposition))

        browser.login().open(self.disposition, view='overview')
        self.assertEquals(['disposition-transition-dispose'],
                          browser.css('.transitions li').text)

    @browsing
    def test_sip_download_is_only_available_in_disposed_state(self, browser):
        self.grant('Archivist', 'Records Manager')
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(['Export appraisal list as excel'],
                          browser.css('ul.actions li').text)

        browser.find('disposition-transition-appraise').click()
        self.assertEquals(['Export appraisal list as excel'],
                          browser.css('ul.actions li').text)

        browser.find('disposition-transition-dispose').click()
        self.assertEquals(['Export appraisal list as excel',
                           'Download disposition package'],
                          browser.css('ul.actions li').text)
        self.assertEquals(
            'http://nohost/plone/disposition-1/ech0160_export',
            browser.find('Download disposition package').get('href'))

    @browsing
    def test_appraisal_list_download_is_always_available(self, browser):
        self.grant('Records Manager')
        browser.login().open(self.disposition, view='overview')
        self.assertEquals(['Export appraisal list as excel'],
                          browser.css('ul.actions li').text)
        self.assertEquals(
            'http://nohost/plone/disposition-1/download_excel',
            browser.find('Export appraisal list as excel').get('href'))

    @browsing
    def test_removal_protocol_is_available_in_closed_state(self, browser):
        self.grant('Editor', 'Records Manager')

        browser.login().open(self.disposition, view='overview')
        self.assertEquals(['Export appraisal list as excel'],
                          browser.css('ul.actions li').text)

        dossier = create(Builder('dossier').as_expired()
                         .within(self.repository))
        disposition_2 = create(Builder('disposition')
                               .having(dossiers=[dossier])
                               .in_state('disposition-state-closed'))
        disposition_2.set_destroyed_dossiers([dossier])
        transaction.commit()

        browser.login().open(disposition_2, view='overview')

        self.assertEquals(['Export appraisal list as excel',
                           'Download removal protocol'],
                          browser.css('ul.actions li').text)
        self.assertEquals(
            'http://nohost/plone/disposition-2/removal_protocol',
            browser.find('Download removal protocol').get('href'))

    @browsing
    def test_states_are_displayed_in_a_wizard_in_the_process_order(self, browser):  # noqa
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            ['disposition-state-in-progress',
             'disposition-state-appraised',
             'disposition-state-disposed',
             'disposition-state-archived',
             'disposition-state-closed'],
            browser.css('.wizard_steps li').text)

    @browsing
    def test_current_state_is_selected(self, browser):
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            ['disposition-state-in-progress'],
            browser.css('.wizard_steps li.selected').text)

    @browsing
    def test_displays_archival_value_for_repositories(self, browser):
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            'Archival value: archival worthy with sampling',
            browser.css('.repository_title .meta').first.text)

    @browsing
    def test_displays_active_and_inactive_dossiers_separately(self, browser):
        browser.login().open(self.disposition, view='overview')

        resolved_list, inactive_list = browser.css('ul.list-group')

        # resolved
        self.assertEquals(
            ['Resolved Dossiers', 'Archive'],
            resolved_list.css('.label h3').text)
        self.assertEquals(
            ['Client1 1 / 1 Dossier A'],
            resolved_list.css('.dispositions h3.title').text)

        # inactive
        self.assertEquals(
            ['Inactive Dossiers', 'Archive'],
            inactive_list.css('.label h3').text)
        self.assertEquals(
            ['Client1 1 / 2 Dossier B'],
            inactive_list.css('.dispositions h3.title').text)

    @browsing
    def test_are_grouped_by_repository_and_sorted(self, browser):
        repository_10 = create(Builder('repository')
                               .titled(u'Repository B')
                               .having(reference_number_prefix=u'10'))
        dossier_c = create(Builder('dossier')
                           .as_expired()
                           .titled(u'Dossier C')
                           .within(repository_10))
        repository_7 = create(Builder('repository')
                              .titled(u'Repository C')
                              .having(reference_number_prefix=u'7'))
        dossier_d = create(Builder('dossier')
                           .as_expired()
                           .titled(u'Dossier D')
                           .within(repository_7))
        dossier_e = create(Builder('dossier')
                           .as_expired()
                           .titled(u'Dossier E')
                           .within(self.repository))

        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[dossier_c,
                                                    dossier_d,
                                                    dossier_e]))

        browser.login().open(self.disposition, view='overview')

        repos = browser.css('.repository-list-item')
        self.assertEquals(
            ['1. Repository A', '7. Repository C', '10. Repository B'],
            repos.css('.repository_title h3').text)

        self.assertEquals(
            ['Dossier E', 'Dossier D', 'Dossier C'],
            repos.css('h3.title a').text)


class TestClosedDispositionOverview(FunctionalTestCase):
    """Test workflow state does not break disposition overviews."""

    def setUp(self):
        super(TestClosedDispositionOverview, self).setUp()

        self.grant(
            'Contributor', 'Editor', 'Reader', 'Reviewer', 'Records Manager')

        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier A',
                                       archival_value='archival worthy'))

        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier B',
                                       archival_value='not archival worthy',))

        self.disposition = create(Builder('disposition')
                                  .in_state('disposition-state-archived')
                                  .having(dossiers=[
                                      self.dossier1,
                                      self.dossier2,
                                      ]))
        self.disposition.mark_dossiers_as_archived()
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')
        transaction.commit()

    @browsing
    def test_dossier_title_is_not_linked(self, browser):
        browser.login().open(self.disposition, view='overview')

        self.assertEquals(
            ['Client1 1 / 1', 'Dossier A', 'Client1 1 / 2', 'Dossier B'],
            browser.css('h3.title span').text)

        self.assertEquals([], browser.css('h3.title a'))

    @browsing
    def test_additional_metadata_is_not_displayed(self, browser):
        browser.login().open(self.disposition, view='overview')

        self.assertEquals([], browser.css('#disposition_overview div.meta'))
