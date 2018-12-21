from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.security import elevated_privileges
from opengever.testing import IntegrationTestCase
import os
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue


class TestDispositionOverview(IntegrationTestCase):

    @browsing
    def test_list_only_all_disposition_dossiers(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals(
            ['Client1 1.1 / 11 Hannah Baufrau',
             'Client1 1.1 / 12 Hans Baumann'],
            browser.css('.dispositions .title').text)

    @browsing
    def test_list_details_for_each_dossiers(self, browser):
        self.login(self.records_manager, browser)

        self.offered_dossier_to_archive.public_trial = 'limited-public'
        ILifeCycle(self.offered_dossier_to_destroy).archival_value_annotation = "In Absprache mit ARCH."

        browser.open(self.disposition, view='overview')

        self.assertEquals(
            ['Period: Jan 01, 2000 - Jan 31, 2000',
             'Period: Jan 01, 2000 - Jan 15, 2000'],
            browser.css('.dispositions .date_period').text)

        self.assertEquals(
            ['Public Trial: limited-public', 'Public Trial: unchecked'],
            browser.css('.dispositions .public_trial').text)

        self.assertEquals(
            ['Archival value: archival worthy',
             'Archival value: not archival worthy ( In Absprache mit ARCH. )'],
            browser.css('.dispositions .archival_value').text)

    @browsing
    def test_archive_button_is_active_depending_on_the_appraisal(self, browser):  # noqa
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals(
            'Archive',
            browser.css('.appraisal-button-group .active')[0].get('title'))
        self.assertEquals(
            "Don't archive",
            browser.css('.appraisal-button-group .active')[1].get('title'))

    @browsing
    def test_appraisal_buttons_are_only_links_in_progress_state(self, browser):
        self.login(self.archivist, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals(
            ['Archive', "Don't archive"],
            [link.get('title') for link
             in browser.css('.appraisal-button-group').first.css('a')])
        browser.find('disposition-transition-appraise').click()

        browser.open(self.disposition, view='overview')
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
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        # first dossier is archival worthy, the second one is unworthy
        self.assertEquals(
            ['Archive', "Don't archive"],
            [link.get('title') for link
             in browser.css('.appraisal-button-group .active')])

        # change appraisal of second dossier to arhival worthy
        button = browser.css('.appraisal-button-group .archive')[1]
        url = browser.css('#disposition_overview').first.get(
            'data-appraisal_update_url')
        data = {'dossier-id': button.get('data-intid'),
                'should_be_archived': button.get('data-archive')}
        browser.open(url, data)

        # Now both are marked as archival worthy
        browser.open(self.disposition, view='overview')
        self.assertEquals(
            ['Archive', 'Archive'],
            [link.get('title') for link
             in browser.css('.appraisal-button-group .active')])

    @browsing
    def test_lists_possible_transitions_in_actionmenu_as_buttons(self, browser):  # noqa
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')
        self.assertEquals([], browser.css('.transitions li').text)

        self.login(self.archivist, browser)
        browser.open(self.disposition, view='overview')
        self.assertEquals(['disposition-transition-appraise',
                           'disposition-transition-refuse'],
                          browser.css('.transitions li').text)

        browser.css('.transitions li a').first.click()
        self.assertEquals('disposition-state-appraised',
                          api.content.get_state(self.disposition))

        browser.open(self.disposition, view='overview')
        self.assertEquals([], browser.css('.transitions li').text)

        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')
        self.assertEquals(['disposition-transition-dispose'],
                          browser.css('.transitions li').text)

    @browsing
    def test_action_availability(self, browser):
        """sip_download is only available in disposed state
        while appraisal list download is always available and
        removal protocol is only available in closed state"""
        api.user.grant_roles(user=self.records_manager, roles=['Archivist'])
        self.login(self.records_manager, browser)

        browser.open(self.disposition, view='overview')

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
            os.path.join(self.disposition.absolute_url(), 'ech0160_export'),
            browser.find('Download disposition package').get('href'))
        self.assertEquals(
            os.path.join(self.disposition.absolute_url(), 'download_excel'),
            browser.find('Export appraisal list as excel').get('href'))

        browser.find('disposition-transition-archive').click()
        self.assertEquals(['Export appraisal list as excel'],
                          browser.css('ul.actions li').text)

        browser.find('disposition-transition-close').click()
        self.assertEquals(['Export appraisal list as excel',
                           'Download removal protocol'],
                          browser.css('ul.actions li').text)
        self.assertEquals(
            os.path.join(self.disposition.absolute_url(), 'removal_protocol'),
            browser.find('Download removal protocol').get('href'))

    @browsing
    def test_states_are_displayed_in_a_wizard_in_the_process_order(self, browser):  # noqa
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals(
            ['disposition-state-in-progress',
             'disposition-state-appraised',
             'disposition-state-disposed',
             'disposition-state-archived',
             'disposition-state-closed'],
            browser.css('.wizard_steps li').text)

    @browsing
    def test_current_state_is_selected(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals(
            ['disposition-state-in-progress'],
            browser.css('.wizard_steps li.selected').text)

    @browsing
    def test_displays_archival_value_for_repositories(self, browser):
        self.login(self.records_manager, browser)
        ILifeCycle(self.leaf_repofolder).archival_value = ARCHIVAL_VALUE_SAMPLING

        browser.open(self.disposition, view='overview')

        self.assertEquals(
            'Archival value: archival worthy with sampling',
            browser.css('.repository_title .meta').first.text)

    @browsing
    def test_displays_active_and_inactive_dossiers_separately(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        resolved_list, inactive_list = browser.css('ul.list-group')

        # resolved
        self.assertEquals(
            ['Resolved Dossiers', 'Archive'],
            resolved_list.css('.label h3').text)
        self.assertEquals(
            ['Client1 1.1 / 11 Hannah Baufrau'],
            resolved_list.css('.dispositions h3.title').text)

        # inactive
        self.assertEquals(
            ['Inactive Dossiers', 'Archive'],
            inactive_list.css('.label h3').text)
        self.assertEquals(
            ['Client1 1.1 / 12 Hans Baumann'],
            inactive_list.css('.dispositions h3.title').text)

    @browsing
    def test_does_not_show_transfer_number_edit_button_when_readonly(self, browser):
        self.login(self.records_manager, browser)
        self.disposition.transfer_number = 'Ablieferung 2013-44'
        browser.open(self.disposition, view='overview')

        self.assertEquals(['Ablieferung 2013-44'],
                          browser.css('div.metadata #transfer-number-value').text)
        self.assertEquals([],
                          browser.css('div.metadata .edit_transfer_number').text)

    @browsing
    def test_shows_transfer_number_in_text_field_when_editable(self, browser):
        self.login(self.archivist, browser)
        self.disposition.transfer_number = 'Ablieferung 2013-44'
        browser.open(self.disposition, view='overview')

        self.assertEquals(['Ablieferung 2013-44'],
                          browser.css('div.metadata #transfer-number-value').text)
        self.assertEquals(['Edit'],
                          browser.css('div.metadata .edit_transfer_number').text)

    @browsing
    def test_are_grouped_by_repository_and_sorted(self, browser):
        self.login(self.records_manager, browser)
        repository_10 = create(Builder('repository')
                               .titled(u'Repository B')
                               .having(reference_number_prefix=u'10'))
        dossier_c = create(Builder('dossier')
                           .as_expired()
                           .titled(u'Dossier C')
                           .within(repository_10))

        dossier_d = create(Builder('dossier')
                           .as_expired()
                           .titled(u'Dossier D')
                           .within(self.empty_repofolder))

        # We change the former end state of the offered_dossier_to_destroy,
        # dossiers that were inactive are displayed separately.
        api.content.transition(self.offered_dossier_to_destroy, transition="dossier-transition-offered-to-resolved")
        api.content.transition(self.offered_dossier_to_destroy, transition="dossier-transition-offer")
        intids = getUtility(IIntIds)
        self.disposition.dossiers += [RelationValue(intids.getId(dossier_c)), RelationValue(intids.getId(dossier_d))]

        browser.open(self.disposition, view='overview')

        repos = browser.css('.repository-list-item')
        self.assertEquals(
            [u'1.1. Vertr\xe4ge und Vereinbarungen',
             u'2. Rechnungspr\xfcfungskommission',
             '10. Repository B'],
            repos.css('.repository_title h3').text)

        self.assertEquals(
            ['Hannah Baufrau', 'Hans Baumann', 'Dossier D', 'Dossier C'],
            repos.css('h3.title a').text)


class TestClosedDispositionOverview(IntegrationTestCase):

    def setUp(self):
        super(TestClosedDispositionOverview, self).setUp()
        with elevated_privileges():
            api.content.transition(obj=self.disposition, transition='disposition-transition-appraise')
            api.content.transition(obj=self.disposition, transition='disposition-transition-dispose')
            api.content.transition(obj=self.disposition, transition='disposition-transition-archive')
            api.content.transition(obj=self.disposition, transition='disposition-transition-close')

    @browsing
    def test_dossier_title_is_not_linked(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals(
            ['Client1 1.1 / 11', 'Hannah Baufrau', 'Client1 1.1 / 12', 'Hans Baumann'],
            browser.css('h3.title span').text)

        self.assertEquals([], browser.css('h3.title a'))

    @browsing
    def test_additional_metadata_is_not_displayed(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='overview')

        self.assertEquals([], browser.css('#disposition_overview div.meta'))
