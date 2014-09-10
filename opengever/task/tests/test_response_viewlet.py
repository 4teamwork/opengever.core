from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestResponseViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestResponseViewlet, self).setUp()

        self.dossier = create(Builder('dossier'))
        self.task = create(Builder('task')
                           .having(task_type='comment'))

    def add_sample_answer(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')
        browser.css('#task-transition-open-in-progress').first.click()
        browser.fill({'Response': u'Sample response'})
        browser.css('#form-buttons-save').first.click()
        browser.open(self.task, view='tabbedview_view-overview')

    @browsing
    def test_task_history(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')

        self.assertEqual(1, len(browser.css('#task-responses div.answer')))

        self.add_sample_answer(browser)

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEqual(2, len(browser.css('#task-responses div.answer')))

    @browsing
    def test_progress_starts_with_created_answer(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')

        answer = browser.css('div.answers .answer').first
        self.assertEqual('Created by Test User (test_user_1_)',
                         answer.css('h3').first.text)
        self.assertEqual('http://nohost/plone/@@user-details/test_user_1_',
                         answer.css('h3 a').first.get('href'))

    @browsing
    def test_answer_contains_response_description(self, browser):
        self.add_sample_answer(browser)
        answer = browser.css('div.answers .answer').first
        self.assertEqual('Accepted by Test User (test_user_1_)',
                         answer.css('h3').first.text)
        self.assertEqual('http://nohost/plone/@@user-details/test_user_1_',
                         answer.css('h3 a').first.get('href'))

    @browsing
    def test_answer_contains_response_text(self, browser):
        self.add_sample_answer(browser)

        answer = browser.css('div.answers .answer').first
        self.assertEqual(u'Sample response', answer.css('.text').first.text)

    @browsing
    def test_manage_actions_are_not_shown_for_default_user(self, browser):
        self.add_sample_answer(browser)

        self.assertEqual([], browser.css('.manageActions .delete'))
        self.assertEqual([], browser.css('.manageActions .edit'))

    @browsing
    def test_manage_actions_are_shown_for_managers(self, browser):
        self.grant('Manager')
        self.add_sample_answer(browser)

        self.assertEqual('Delete',
                         browser.css('.manageActions .delete').first.text)
        self.assertEqual('Edit',
                         browser.css('.manageActions .edit').first.text)
