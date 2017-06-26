from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.meeting.wrapper import MemberWrapper
from opengever.testing import FunctionalTestCase


class TestPathBar(FunctionalTestCase):

    def setUp(self):
        super(TestPathBar, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.root = create(Builder('repository_root').titled(u'Repository'))
        self.repo = create(Builder('repository')
                           .within(self.root)
                           .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .titled(u'Dossier 1'))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repo))

    @browsing
    def test_committee_pathbar_is_correct(self, browser):
        container = create(Builder('committee_container'))
        committee = create(Builder('committee').within(container))
        meeting = create(Builder('meeting')
                         .having(committee=committee.load_model())
                         .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url())
        self.assertEqual(
            ['Client1', 'opengever-meeting-committeecontainer',
             'My Committee', u'C\xf6mmunity meeting'],
            browser.css('#portal-breadcrumbs a').text)

    @browsing
    def test_member_pathbar_is_correct(self, browser):
        container = create(Builder('committee_container'))
        member = create(Builder('member'))

        browser.login().open(member.get_url(container))
        self.assertEqual(
            [u'Client1',
             u'opengever-meeting-committeecontainer',
             u'M\xfcller Peter'],
            browser.css('#portal-breadcrumbs a').text)

    @browsing
    def test_membership_pathbar_is_correct(self, browser):
        container = create(Builder('committee_container'))
        committee = create(Builder('committee').within(container))
        committee_model = committee.load_model()
        member = create(Builder('member'))
        membership = create(Builder('membership')
                            .having(member=member,
                                    committee=committee_model,
                                    date_from=date(2014, 1, 1),
                                    date_to=date(2015, 1, 1)))

        wrapped_member = MemberWrapper.wrap(container, member)
        browser.login().open(membership.get_url(wrapped_member))
        self.assertEqual(
            [u'Client1',
             u'opengever-meeting-committeecontainer',
             u'M\xfcller Peter',
             u'M\xfcller Peter, Jan 01, 2014 - Jan 01, 2015'],
            browser.css('#portal-breadcrumbs a').text)
