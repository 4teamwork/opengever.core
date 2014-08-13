from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from ftw.testbrowser import browsing


class TestResponseViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestResponseViewlet, self).setUp()

        self.dossier = create(Builder('dossier'))
        self.task = create(Builder('task').having(task_type='comment'))

    @browsing
    def test_task_history(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')
        self.assertEqual(1, len(browser.css('#task-responses div.answer')))

        browser.css('#task-transition-open-tested-and-closed').first.click()
        browser.css('#form-buttons-save').first.click()

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEqual(2, len(browser.css('#task-responses div.answer')))
