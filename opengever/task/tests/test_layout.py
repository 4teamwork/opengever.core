from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestTaskLayout(FunctionalTestCase):

    def setUp(self):
        super(TestTaskLayout, self).setUp()
        self.task = create(Builder('task'))

    @browsing
    def test_body_class_is_default_for_main_taks(self, browser):
        browser.login().open(self.task)

        self.assertEquals(
            'template-tabbed_view portaltype-opengever-task-task site-plone section-task-1 icons-on',
            browser.css('body').first.get('class'))

    @browsing
    def test_body_class_is_extended_with_subtask_class_for_subtasks(self, browser):
        subtask = create(Builder('task').within(self.task))

        browser.login().open(subtask)

        self.assertEquals(
            'template-tabbed_view portaltype-opengever-task-task site-plone section-task-1 icons-on subtask',
            browser.css('body').first.get('class'))
