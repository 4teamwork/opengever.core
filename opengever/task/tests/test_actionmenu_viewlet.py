from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from ftw.testbrowser import browsing


class TestActionmenuViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestActionmenuViewlet, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.dossier = create(Builder('dossier'))
        self.task = create(Builder('task').having(task_type='comment'))

    @browsing
    def test_action_menu_viewlet(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')
        self.assertGreater(len(browser.css('#action-menu li')), 1,
                           'no action menu entries found')
