from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestCommitteeOverview(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeOverview, self).setUp()
        self.committee = create(Builder('committee'))
        self.committee_model = self.committee.load_model()

    @browsing
    def test_membership_box_shows_only_active_members(self, browser):
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        peter = create(Builder('member'))
        hans = create(Builder('member')
                      .having(firstname=u'Hans', lastname=u'M\xfcller'))
        james = create(Builder('member')
                       .having(firstname=u'James', lastname=u'Bond'))

        create(Builder('membership')
               .having(member=peter, committee=self.committee_model,
                       date_from=yesterday, date_to=tomorrow))
        create(Builder('membership')
               .having(member=hans, committee=self.committee_model,
                       date_from=yesterday, date_to=tomorrow))
        create(Builder('membership')
               .having(member=james, committee=self.committee_model,
                       date_from=date(2014, 1, 1), date_to=date(2015, 1, 1)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(['Peter Meier', u'Hans M\xfcller'],
                          browser.css('#current_membersBox li:not(.moreLink)').text)

    @browsing
    def test_member_is_linked_correctly(self, browser):
        peter = create(Builder('member'))

        create(Builder('membership')
               .having(member=peter, committee=self.committee_model,
                       date_from=date.today() - timedelta(days=1),
                       date_to=date.today() + timedelta(days=1)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/committee-1/member/1',
            browser.css('#current_membersBox li a').first.get('href'))

    @browsing
    def test_upcoming_meetings_box_only_lists_meetings_in_the_future(self, browser):
        create(Builder('meeting')
               .having(committee=self.committee_model,
                       start=datetime.now() - timedelta(days=1)))
        meeting2 = create(Builder('meeting')
                          .having(committee=self.committee_model,
                                  start=datetime.now() + timedelta(hours=1)))
        meeting3 = create(Builder('meeting')
                          .having(committee=self.committee_model,
                                  start=datetime.now() + timedelta(days=1)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [meeting2.get_title(), meeting3.get_title()],
            browser.css('#upcoming_meetingsBox li:not(.moreLink) a').text)

    @browsing
    def test_upcoming_meetings_box_only_lists_meetings_of_the_current_committee(self, browser):
        committee_b = create(Builder('committee'))
        committee_b_model = committee_b.load_model()
        meeting1 = create(Builder('meeting')
                          .having(committee=self.committee_model,
                                  start=datetime.now() + timedelta(hours=1)))
        create(Builder('meeting')
               .having(committee=committee_b_model,
                       start=datetime.now() + timedelta(hours=1)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [meeting1.get_title()],
            browser.css('#upcoming_meetingsBox li:not(.moreLink) a').text)

    @browsing
    def test_meetings_are_linked_correctly(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model,
                                 start=datetime.now() + timedelta(days=1)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            meeting.get_url(),
            browser.css('#upcoming_meetingsBox li a').first.get('href'))

    @browsing
    def test_meetings_are_limited_to_ten_entries(self, browser):
        for i in range(0, 12):
            create(Builder('meeting')
                   .having(committee=self.committee_model,
                           start=datetime.now() + timedelta(days=i)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        meetings = browser.css('#upcoming_meetingsBox li:not(.moreLink) a')
        self.assertEquals(10, len(meetings))

    @browsing
    def test_meetings_are_limited_to_ten_entries(self, browser):
        for i in range(0, 12):
            create(Builder('meeting')
                   .having(committee=self.committee_model,
                           start=datetime.now() + timedelta(days=i)))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        meetings = browser.css('#upcoming_meetingsBox li:not(.moreLink) a')
        self.assertEquals(10, len(meetings))

    @browsing
    def test_proposal_box_only_lists_unscheduled_proposals(self, browser):
        proposal_a = create(Builder('proposal')
                            .having(title=u'Proposal A',
                                    committee=self.committee_model))
        create(Builder('submitted_proposal').submitting(proposal_a))

        proposal_b = create(Builder('proposal')
                            .having(title=u'Proposal B',
                                    committee=self.committee_model))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            [u'Proposal A'],
            browser.css('#unscheduled_proposalsBox li:not(.moreLink) a').text)

    @browsing
    def test_proposals_are_linked_correctly(self, browser):
        proposal_a = create(Builder('proposal')
                            .having(title=u'Mach doch',
                                    committee=self.committee_model))
        create(Builder('submitted_proposal').submitting(proposal_a))

        browser.login().open(self.committee, view='tabbedview_view-overview')

        self.assertEquals(
            'http://example.com/committee-1/submitted-proposal-1',
            browser.css('#unscheduled_proposalsBox li a').first.get('href'))
