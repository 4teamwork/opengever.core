from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestResponseViewlet(IntegrationTestCase):

    def add_sample_answer(self, browser, response=u'Sample response'):
        browser.css('#task-transition-resolved-tested-and-closed').first.click()
        browser.fill({'Response': response})
        browser.css('#form-buttons-save').first.click()
        browser.open(self.subtask, view='tabbedview_view-overview')

    @browsing
    def test_task_history(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.assertEqual(1, len(browser.css('#task-responses div.answer')))

        self.add_sample_answer(browser)

        browser.open(self.subtask, view='tabbedview_view-overview')
        self.assertEqual(2, len(browser.css('#task-responses div.answer')))

    @browsing
    def test_progress_starts_with_created_answer(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        answer = browser.css('div.answers .answer').first
        self.assertEqual('Created by Ziegler Robert (robert.ziegler)',
                         answer.css('h3').first.text)
        self.assertEqual('http://nohost/plone/kontakte/user-robert.ziegler/view',
                         answer.css('h3 a').first.get('href'))

    @browsing
    def test_answer_contains_response_description(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.add_sample_answer(browser)
        answer = browser.css('div.answers .answer').first
        self.assertEqual('Closed by Ziegler Robert (robert.ziegler)',
                         answer.css('h3').first.text)
        self.assertEqual('http://nohost/plone/kontakte/user-robert.ziegler/view',
                         answer.css('h3 a').first.get('href'))

    @browsing
    def test_response_description_is_web_intelligent_transformed(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.add_sample_answer(
            browser, response=u'Anfrage:\r\n\r\n\r\nhttp://www.example.org/')

        self.assertEqual(
            'Anfrage:\n\n\nhttp://www.example.org/',
            browser.css('.answers .text').first.text)
        link = browser.css('.answers .text a').first
        self.assertEqual('http://www.example.org/', link.text)
        self.assertEqual('http://www.example.org/', link.get('href'))

    @browsing
    def test_response_description_is_xss_safe(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.add_sample_answer(
            browser,
            response='<img src="http://not.found/" '
            'onerror="script:alert(\'XSS\');" />')

        self.assertEqual(
            u'&lt;img src="http://not.found/" onerror="script:alert(\'XSS\');" /&gt;',
            browser.css('.answers .text').first.innerHTML)

    @browsing
    def test_answer_contains_response_text(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.add_sample_answer(browser)

        answer = browser.css('div.answers .answer').first
        self.assertEqual(u'Sample response', answer.css('.text').first.text)

    @browsing
    def test_manage_actions_are_not_shown_for_default_user(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.add_sample_answer(browser)

        self.assertEqual([], browser.css('.manageActions .delete'))
        self.assertEqual([], browser.css('.manageActions .edit'))

    @browsing
    def test_manage_actions_are_shown_for_managers(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')

        self.add_sample_answer(browser)

        self.assertEqual('Delete',
                         browser.css('.manageActions .delete').first.text)
        self.assertEqual('Edit',
                         browser.css('.manageActions .edit').first.text)
