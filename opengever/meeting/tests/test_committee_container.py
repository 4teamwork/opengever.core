from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.date_time import utcnow_tz_aware
from opengever.testing import add_languages
from opengever.testing import IntegrationTestCase


class TestCommitteeContainer(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_supports_translated_title(self, browser):
        self.login(self.manager, browser)
        add_languages(['de-ch', 'fr-ch'])
        browser.open()
        factoriesmenu.add('Committee Container')
        browser.fill({'Title (German)': u'Sitzungen',
                      'Title (French)': u's\xe9ance',
                      'Protocol template': self.sablon_template,
                      'Excerpt template': self.sablon_template,
                      'Table of contents template': self.sablon_template}).save()
        statusmessages.assert_no_error_messages()

        browser.find(u'Fran\xe7ais').click()
        self.assertEquals(u's\xe9ance', browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals(u'Sitzungen', browser.css('h1').first.text)

    def test_get_toc_template(self):
        self.login(self.manager)

        self.assertIsNone(self.committee_container.toc_template)
        self.assertIsNone(self.committee_container.get_toc_template())

        self.committee_container.toc_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee_container.get_toc_template())

    def test_portlets_inheritance_is_blocked(self):
        self.login(self.manager)
        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', self.committee_container)


class TestCommitteesTab(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_shows_albhabetically_sorted_committees_in_boxes(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')

        self.assertEquals(
            [u'Kommission f\xfcr Verkehr',
             u'Rechnungspr\xfcfungskommission'],
            browser.css('#committees_view .committee_box h2').text)

    @browsing
    def test_can_only_see_committees_for_corresponding_group(self, browser):
        with self.login(self.administrator):
            create(Builder('committee')
                   .within(self.committee_container)
                   .titled(u'Invisible'))

        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')
        self.assertEquals(
            [u'Kommission f\xfcr Verkehr',
             u'Rechnungspr\xfcfungskommission'],
            browser.css('#committees_view .committee_box h2').text)

    @browsing
    def test_tabbedview_text_filter(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees',
                     data={'searchable_text': 'Rechnung'})

        self.assertEquals(
            [u'Rechnungspr\xfcfungskommission'],
            browser.css('#committees_view .committee_box h2').text)

    @browsing
    def test_text_filter_ignores_trailing_asterisk(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees',
                     data={'searchable_text': 'Rechnung*'})

        self.assertEquals(
            [u'Rechnungspr\xfcfungskommission'],
            browser.css('#committees_view .committee_box h2').text)

    @browsing
    def test_list_only_active_committees_by_default(self, browser):
        with self.login(self.committee_responsible, browser):
            browser.open(self.empty_committee)
            editbar.menu_option('Actions', 'deactivate').click()

        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')
        self.assertEquals(
            [u'Rechnungspr\xfcfungskommission'],
            browser.css('#committees_view .committee_box h2').text)

    @browsing
    def test_list_all_committees_when_selecting_all_filter(self, browser):
        with self.login(self.committee_responsible, browser):
            browser.open(self.empty_committee)
            editbar.menu_option('Actions', 'deactivate').click()

        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees',
                     data={'committee_state_filter': 'filter_all'})

        self.assertEquals(
            [u'Kommission f\xfcr Verkehr',
             u'Rechnungspr\xfcfungskommission'],
            browser.css('#committees_view .committee_box h2').text)

    @browsing
    def test_committe_box_has_state_class(self, browser):
        with self.login(self.committee_responsible, browser):
            browser.open(self.empty_committee)
            editbar.menu_option('Actions', 'deactivate').click()

        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees',
                     data={'committee_state_filter': 'filter_all'})

        self.assertEquals(
            'committee_box inactive',
            browser.css('#committees_view .committee_box')[0].get('class'))
        self.assertEquals(
            'committee_box active',
            browser.css('#committees_view .committee_box')[1].get('class'))

    @browsing
    def test_committee_is_linked_correctly(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')

        title = browser.css('#committees_view .committee_box a').first

        self.assertEquals(u'Kommission f\xfcr Verkehr', title.text)
        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-2',
            title.get('href'))

    @browsing
    def test_unscheduled_proposal_number(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')

        self.assertEquals(
            ['New unscheduled proposals: 0',
             'New unscheduled proposals: 2'],
            browser.css('#committees_view .unscheduled_proposals').text)

    @browsing
    def test_unscheduled_proposal_number_link(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')

        link = browser.css('#committees_view .unscheduled_proposals a')[1]

        self.assertEquals('2', link.text)
        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1#submittedproposals',
            link.get('href'))

    @browsing
    def test_unscheduled_proposal_number_class(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')

        links = browser.css('#committees_view .unscheduled_proposals a')

        self.assertEquals('0', links[0].text)
        self.assertEquals('number', links[0].get('class'))
        self.assertEquals('2', links[1].text)
        self.assertEquals('number unscheduled_number', links[1].get('class'))

    @browsing
    def test_meetings_display(self, browser):
        with self.login(self.committee_responsible):
            start = utcnow_tz_aware() + timedelta(days=5)

            meeting_dossier = create(
                Builder('meeting_dossier')
                .within(self.leaf_repofolder)
                .titled(u'Sitzungsdossier f')
                .having(start=start.date(),
                        responsible=self.committee_responsible.getId()))
            meeting = create(
                Builder('meeting')
                .having(title=u'f. Sitzung der Rechnungspr\xfcfungskommission',
                        committee=self.committee.load_model(),
                        location=u'B\xfcren an der Aare',
                        start=start)
                .link_with(meeting_dossier))

        self.login(self.meeting_user, browser)
        browser.open(self.committee_container,
                     view='tabbedview_view-committees')

        self.assertEquals(
            ['Last Meeting: Sep 12, 2016',
             'Next Meeting: {}'.format(meeting.get_date())],
            browser.css('#committees_view .meetings li').text)

        last_meeting = browser.css('#committees_view .meetings li a')[0]
        next_meeting = browser.css('#committees_view .meetings li a')[1]

        self.assertEquals(self.meeting.model.get_url(),
                          last_meeting.get('href'))
        self.assertEquals(meeting.get_url(), next_meeting.get('href'))
