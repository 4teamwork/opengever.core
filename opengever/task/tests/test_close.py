from ftw.testbrowser import browsing
from opengever.task.adapters import IResponseContainer
from opengever.testing import IntegrationTestCase
from plone import api


class TestClosingForInformationTask(IntegrationTestCase):

    @browsing
    def test_closes_task_directly_when_no_document_is_selected(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.info_task, view=u'tabbedview_view-overview')
        browser.click_on('task-transition-open-tested-and-closed')
        browser.fill({'Response': u'OK!'})
        browser.click_on('Save')
        self.assertEquals('task-state-tested-and-closed', api.content.get_state(self.info_task))
        response = IResponseContainer(self.info_task)[-1]
        self.assertEquals(u'OK!', response.text)
        self.assertEquals('task-transition-open-tested-and-closed', response.transition)

    @browsing
    def test_closes_task_when_remote_close_view_is_called(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.info_task,
            data={'text': u'Danke sch\xf6n'},
            send_authenticator=True,
            view=u'close-task-wizard-remote_close',
        )
        self.assertEquals('OK', browser.contents)

        self.assertEquals('task-state-tested-and-closed',
                          api.content.get_state(self.info_task))
        response = IResponseContainer(self.info_task)[-1]
        self.assertEquals(u'Danke sch\xf6n', response.text)
        self.assertEquals('task-transition-open-tested-and-closed',
                          response.transition)

    @browsing
    def test_ignores_conflict_retries(self, browser):
        data = {'text': u'Danke sch\xf6n'}
        self.login(self.regular_user, browser)
        browser.open(self.info_task, data=data, send_authenticator=True, view=u'close-task-wizard-remote_close')
        self.assertEquals('OK', browser.contents)
        browser.open(self.info_task, data=data, send_authenticator=True, view=u'close-task-wizard-remote_close')
        self.assertEquals('OK', browser.contents)
