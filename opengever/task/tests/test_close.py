from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from opengever.task.adapters import IResponseContainer

class TestClosingForInformationTask(FunctionalTestCase):

    def setUp(self):
        super(TestClosingForInformationTask, self).setUp()
        additional_admin_unit = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit')
               .with_default_groups()
               .having(admin_unit=additional_admin_unit)
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
