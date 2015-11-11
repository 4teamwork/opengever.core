from ftw.builder import Builder
from ftw.builder import create
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
                                      responsible='hugo.boss'))
