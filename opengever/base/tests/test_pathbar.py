from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPathBar(FunctionalTestCase):

    def setUp(self):
        super(TestPathBar, self).setUp()

        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                              .within(repo)
                              .titled(u'Dossier 1'))

    @browsing
    def test_first_part_is_org_unit_title(self, browser):
        browser.login().open(self.dossier)

        breadcrumb_links = browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Client1', 'Repository', '1. Testposition', 'Dossier 1'],
            breadcrumb_links.text)

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
                         .having(committee=committee.load_model(),
                                 date=date(2010, 1, 1)))

        browser.login().open(view=meeting.physical_path)
        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(meeting.get_url(), last_link.node.attrib['href'])
        self.assertEqual(meeting.get_title(), last_link.node.text)
