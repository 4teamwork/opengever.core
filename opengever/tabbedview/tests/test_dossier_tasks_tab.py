from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDossierTaskTabbedview(FunctionalTestCase):

    def setUp(self):
        super(TestDossierTaskTabbedview, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())
        self.dossier = create(Builder('dossier'))
        self.dossier2 = create(Builder('dossier'))
        self.task = create(Builder('task').within(self.dossier))
        self.task2 = create(Builder('task').within(self.dossier2))

    def get_tabbed_view(self, name):
        view = self.dossier.restrictedTraverse('tabbedview_view-tasks')
        view.update()
        return view

    @browsing
    def test_task_listing_returns_only_dossier_tasks(self, browser):
        view = self.get_tabbed_view('tabbedview_view-tasks')
        self.assertItemsEqual([self.task.get_sql_object()], view.contents)
