from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.interfaces import IReferenceNumber
from opengever.task.browser.transitioncontroller import RequestChecker
from opengever.testing import IntegrationTestCase
from plone import api


class TestResolveMultiAdminUnitTasks(IntegrationTestCase):

    def setUp(self):
        super(TestResolveMultiAdminUnitTasks, self).setUp()
        self.org_is_remote = RequestChecker.is_remote
        RequestChecker.is_remote = True

    def tearDown(self):
        super(TestResolveMultiAdminUnitTasks, self).tearDown()
        RequestChecker.is_remote = self.org_is_remote

    @browsing
    def test_resolve_copies_document(self, browser):
        self.login(self.regular_user, browser=browser)

        for task in (self.private_task, self.inbox_task):
            task.task_type = 'correction'
            task.responsible_client = 'rk'
            task.responsible = self.regular_user.id
            self.set_workflow_state('task-state-in-progress', task)
            task.sync()

        self.register_successor(self.private_task, self.inbox_task)
        browser.open(self.inbox_task, view='tabbedview_view-overview')
        browser.click_on('task-transition-in-progress-resolved')

        document_label = '%s (%s, %s)' % (
            self.document.Title(),
            IReferenceNumber(self.document).get_number(),
            aq_parent(aq_inner(self.document)).Title())
        browser.fill({'Documents to deliver': document_label, 'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual('task-state-resolved',
                         api.content.get_state(self.inbox_task))
        self.assertEqual(
            ['The documents were delivered to the issuer and the tasks were completed.'],
            info_messages())
        self.assertEqual(1, len(self.private_task.listFolderContents()))
        copied_doc, = self.private_task.listFolderContents()
        self.assertEqual(u'RE: Vertr\xe4gsentwurf', copied_doc.title)
