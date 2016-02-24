from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.tests.test_overview import TestOverview


class TestMeetingDossierOverview(TestOverview):

    def _setup_dossier(self):
        self.root = create(Builder('repository_root').titled(u'Repository'))
        self.repo = create(Builder('repository')
                           .within(self.root)
                           .titled(u'Testposition'))
        self.dossier = create(Builder('meeting_dossier')
                              .titled(u'Testdossier')
                              .having(description=u'Hie hesch e beschribig',
                                      responsible='hugo.boss')
                              .within(self.repo))
        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(self.container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model())
                              .link_with(self.dossier))

    @browsing
    def test_meeting_is_linked_on_overview(self, browser):
        browser.login().open(self.dossier, view='tabbedview_view-overview')

        link_node = browser.find(u'C\xf6mmunity meeting')
        self.assertEqual(self.meeting.get_url(), link_node.get('href'))
