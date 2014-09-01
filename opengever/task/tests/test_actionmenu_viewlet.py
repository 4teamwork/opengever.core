from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestActionmenuViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestActionmenuViewlet, self).setUp()

        create(Builder('ogds_user').id('hugo.boss'))

        self.task = create(Builder('task')
                           .having(issuer='hugo.boss',
                                   responsible=TEST_USER_ID,
                                   task_type='comment'))

    @browsing
    def test_action_menu_viewlet(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')
        self.assertGreater(len(browser.css('#action-menu li')), 1,
                           'no action menu entries found')

    @browsing
    def test_agency_actions_are_display_separately(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')

        self.assertEquals(
            ['task-transition-open-in-progress',
             'task-transition-open-rejected',
             'task-transition-open-resolved',
             'task-transition-reassign'],
            browser.css('ul.regular_buttons a').text)

        self.assertEquals(
            ['task-transition-open-cancelled',
             'task-transition-open-tested-and-closed'],
            browser.css('dl.agency_buttons ul a').text)

    @browsing
    def test_agency_button_is_hidden_when_no_agency_actions_are_available(self, browser):
        task = create(Builder('task')
                           .having(issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID,
                                   task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals([], browser.css('dl.agency_buttons'))
