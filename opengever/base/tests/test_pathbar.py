from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPathBar(FunctionalTestCase):

    def setUp(self):
        super(TestPathBar, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.root = create(Builder('repository_root').titled(u'Repository'))
        self.repo = create(Builder('repository')
                           .within(self.root)
                           .titled(u'Testposition'))
        self.subrepo = create(Builder('repository')
                              .within(self.repo)
                              .titled(u'Subposition'))
        self.dossier = create(Builder('dossier')
                              .within(self.subrepo)
                              .titled(u'Dossier 1'))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.subrepo))

    @browsing
    def test_first_part_is_org_unit_title(self, browser):
        browser.login().open(self.dossier)

        first_part = browser.css('#portal-breadcrumbs li a')[0]
        self.assertEquals('Client1', first_part.text)
        self.assertEquals(self.portal.absolute_url(), first_part.get('href'))

    @browsing
    def test_contains_contenttype_icon_class(self, browser):
        browser.login().open(self.dossier)

        self.assertEquals(
            ['contenttype-plone-site',
             'contenttype-opengever-repository-repositoryfolder',
             'contenttype-opengever-repository-repositoryfolder',
             'contenttype-opengever-repository-repositoryroot',
             'contenttype-opengever-dossier-businesscasedossier'],
            [crumb.get('class') for crumb in
             browser.css('#portal-breadcrumbs li a i')])

    @browsing
    def test_repositories_are_grouped_in_a_sublist(self, browser):
        browser.login().open(self.dossier)

        self.assertEquals(
            ['Client1',
             '1.1. Subposition', '1. Testposition', 'Repository',
             'Dossier 1'],
            browser.css('#portal-breadcrumbs li a').text)

        self.assertEquals(['1. Testposition', 'Repository'],
                          browser.css('#portal-breadcrumbs li ul a').text)

    @browsing
    def test_last_part_is_linked(self, browser):
        browser.login().open(self.dossier)

        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(self.dossier.absolute_url(),
                         last_link.node.attrib['href'])

    @browsing
    def test_proposal_is_linked_with_title(self, browser):
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled('My Proposal'))

        browser.login().open(proposal)
        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(proposal.absolute_url(),
                         last_link.node.attrib['href'])
        self.assertEqual('My Proposal', last_link.text)

    @browsing
    def test_meeting_is_linked_with_title(self, browser):
        container = create(Builder('committee_container'))
        committee = create(Builder('committee').within(container))
        meeting = create(Builder('meeting')
                         .having(committee=committee.load_model())
                         .link_with(self.meeting_dossier))

        self.grant('MeetingUser', on=container)
        self.grant('CommitteeMember', on=committee)
        browser.login().open(meeting.get_url())
        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1',
            last_link.get('href'))

        self.assertEqual(meeting.get_title(), last_link.text)
