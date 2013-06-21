from Products.CMFCore.utils import getToolByName
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized
import transaction


class TestTaskWorkflow(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestTaskWorkflow, self).setUp()
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')

    def test_document_in_a_closed_tasks_are_still_editable(self):
        self.grant('Editor')
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        document = create(Builder('document')
                          .within(task)
                          .with_default_values())

        self.wf_tool.doActionFor(
            task, 'task-transition-open-tested-and-closed')

        self.browser.open('%s/edit' % (document.absolute_url()))
        self.browser.fill({'Title': 'New Title'})
        self.browser.click('Save')

    def test_editing_document_inside_a_task_inside_a_closed_dossier_raise_unauthorized(self):
        self.grant('Editor', 'Reviewer')
        dossier = create(Builder('dossier'))
        task = create(Builder('task')
                      .within(dossier)
                      .having(issuer=TEST_USER_ID, responsible=TEST_USER_ID))
        document = create(Builder('document')
                          .within(task)
                          .with_default_values())

        self.wf_tool.doActionFor(task,
                                 'task-transition-open-tested-and-closed')
        self.wf_tool.doActionFor(dossier, 'dossier-transition-resolve')
        transaction.commit()

        with self.assertRaises(Unauthorized) as cm:
            self.browser.open('%s/edit' % (document.absolute_url()))

        self.assertEquals(
            'You are not authorized to access this resource.',
            str(cm.exception))
