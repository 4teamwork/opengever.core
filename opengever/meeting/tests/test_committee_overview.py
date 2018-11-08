from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import localized_datetime


class TestCommitteeOverview(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_shows_current_period_box(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEqual(
            u'2016 (Jan 01, 2016 - Dec 31, 2016)',
            browser.css('#periodBox li').first.text)

    @browsing
    def test_membership_box_shows_only_active_members(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            # create a membership which should not appear
            self.login(self.administrator)
            james = create(Builder('member')
                           .having(firstname=u'James', lastname=u'Bond'))
            create(Builder('membership')
                   .having(member=james,
                           committee=self.committee,
                           date_from=localized_datetime(2014, 1, 1),
                           date_to=localized_datetime(2015, 1, 1)))

            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [u'Sch\xf6ller Heidrun', 'Wendler Jens', u'W\xf6lfl Gerda'],
            browser.css('#current_membersBox li:not(.moreLink)').text)

    @browsing
    def test_membership_shows_members_alphabetically(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.administrator)
            anton = create(Builder('member')
                           .having(firstname=u'Anton', lastname=u'Andermatt'))
            lucas = create(Builder('member')
                           .having(firstname=u'Lucas', lastname=u'Lenz'))
            kevin = create(Builder('member')
                           .having(firstname=u'Kevin', lastname=u'Kummermuth'))

            create(Builder('membership')
                   .having(member=anton,
                           committee=self.committee,
                           date_from=localized_datetime(2016, 1, 1),
                           date_to=localized_datetime(2017, 1, 1)))

            create(Builder('membership')
                   .having(member=lucas,
                           committee=self.committee,
                           date_from=localized_datetime(2016, 1, 1),
                           date_to=localized_datetime(2017, 1, 1)))

            create(Builder('membership')
                   .having(member=kevin,
                           committee=self.committee,
                           date_from=localized_datetime(2016, 1, 1),
                           date_to=localized_datetime(2017, 1, 1)))

            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        expected_members = [
            'Andermatt Anton',
            'Kummermuth Kevin',
            'Lenz Lucas',
            u'Sch\xf6ller Heidrun',
            'Wendler Jens',
            u'W\xf6lfl Gerda',
            ]
        self.assertEquals(
            expected_members,
            browser.css('#current_membersBox li:not(.moreLink)').text)

    @browsing
    def test_member_is_linked_correctly(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/member-1',
            browser.css('#current_membersBox li a').first.get('href'))

    @browsing
    def test_upcoming_meetings_box_only_lists_meetings_in_the_future(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [u'8. Sitzung der Rechnungspr\xfcfungskommission', u'9. Sitzung der Rechnungspr\xfcfungskommission'],
            browser.css('#upcoming_meetingsBox li:not(.moreLink) a').text)

    @browsing
    def test_closed_meetings_box_only_lists_meetings_in_the_past(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [u'7. Sitzung der Rechnungspr\xfcfungskommission'],
            browser.css('#closed_meetingsBox li:not(.moreLink) a').text)

    @browsing
    def test_meetings_are_linked_correctly(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        link = browser.css('#upcoming_meetingsBox li a').first.get('href')
        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-2/view',
            browser.css('#upcoming_meetingsBox li a').first.get('href'))

    @browsing
    def test_upcoming_meetings_are_limited_to_ten_entries(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.administrator)
            [create(Builder('meeting')
                    .having(committee=self.committee,
                            start=localized_datetime(2016, 1, 10) + timedelta(days=i)))
             for i in range(12)]
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        meetings = browser.css('#upcoming_meetingsBox li:not(.moreLink) a')
        self.assertEquals(10, len(meetings))

    @browsing
    def test_closed_meetings_are_limited_to_ten_entries(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.administrator)
            [create(Builder('meeting')
                    .having(committee=self.committee,
                            start=localized_datetime(2016, 1 ,10) - timedelta(days=i)))
             for i in range(12)]
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        meetings = browser.css('#closed_meetingsBox li:not(.moreLink) a')
        self.assertEquals(10, len(meetings))

    @browsing
    def test_proposal_box_only_lists_unscheduled_proposals(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [u'Vertr\xe4ge'],
            browser.css('#unscheduled_proposalsBox li:not(.moreLink) a').text)

        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.administrator)
            self.schedule_proposal(self.meeting, self.proposal)

            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [],
            browser.css('#unscheduled_proposalsBox li:not(.moreLink) a').text)

    @browsing
    def test_proposals_are_linked_correctly(self, browser):
        with freeze(localized_datetime(2016, 1, 10)):
            self.login(self.committee_responsible, browser)
            browser.open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/submitted-proposal-1',
            browser.css('#unscheduled_proposalsBox li a').first.get('href'))
