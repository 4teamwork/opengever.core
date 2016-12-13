from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.task.adapters import IResponseContainer
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.protect import createToken


class TestClosingForInformationTask(FunctionalTestCase):

    def setUp(self):
        super(TestClosingForInformationTask, self).setUp()
        additional = create(Builder('admin_unit')
                            .having(public_url='http://nohost/plone',
                                    site_url='http://nohost/plone')
                            .id(u'additional'))
        create(Builder('org_unit')
               .with_default_groups()
               .having(admin_unit=additional)
               .id(u'additional'))

    @browsing
    def test_closes_task_directly_when_no_document_is_selected(self, browser):
        document = create(Builder('document'))
        task = create(Builder('task')
                      .having(task_type=u'information',
                              responsible_client='additional',
                              responsible=TEST_USER_ID,
                              relatedItems=[document]))

        browser.login().open(task, view=u'tabbedview_view-overview')
        browser.click_on('task-transition-open-tested-and-closed')
        browser.fill({'Response': u'OK!'})
        browser.click_on('Continue')

        self.assertEquals('task-state-tested-and-closed',
                          api.content.get_state(task))

        response = IResponseContainer(task)[-1]
        self.assertEquals(u'OK!', response.text)
        self.assertEquals('task-transition-open-tested-and-closed',
                          response.transition)

    @browsing
    def test_closes_task_when_remote_close_view_is_called(self, browser):
        task = create(Builder('task')
                      .having(task_type=u'information',
                              responsible_client='additional',
                              responsible=TEST_USER_ID))

        browser.login().open(task,
                             data={'text': u'Danke sch\xf6n',
                                   '_authenticator': createToken()},
                             view=u'close-task-wizard-remote_close')

        self.assertEquals('OK', browser.contents)

        self.assertEquals('task-state-tested-and-closed',
                          api.content.get_state(task))
        response = IResponseContainer(task)[-1]
        self.assertEquals(u'Danke sch\xf6n'.encode('utf-8'), response.text)
        self.assertEquals('task-transition-open-tested-and-closed',
                          response.transition)

    @browsing
    def test_ignores_conflict_retries(self, browser):
        task = create(Builder('task')
                      .having(task_type=u'information',
                              responsible_client='additional',
                              responsible=TEST_USER_ID))

        data = {'text': u'Danke sch\xf6n', '_authenticator': createToken()}
        browser.login().open(task, data=data,
                             view=u'close-task-wizard-remote_close')
        self.assertEquals('OK', browser.contents)

        browser.login().open(task, data=data,
                             view=u'close-task-wizard-remote_close')
        self.assertEquals('OK', browser.contents)
