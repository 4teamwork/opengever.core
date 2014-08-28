from Products.CMFCore.utils import getToolByName
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.testing import FunctionalTestCase
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent, addContentToContainer
from zope.component import createObject
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
import transaction


def create_testobject(parent, ptype, **kwargs):
    createContent(ptype)
    obj = createContent(ptype, **kwargs)
    notify(ObjectCreatedEvent(obj))
    obj = addContentToContainer(parent, obj, checkConstraints=False)
    notify(ObjectAddedEvent(obj))
    return obj


class TestTaskTemplates(FunctionalTestCase):

    def test_adding(self):
        parent = self.layer['portal']

        t1 = create_testobject(
            parent,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 1')

        self.failUnless(ITaskTemplate.providedBy(t1))

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplate')

        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplate')
        schema = fti.lookupSchema()

        self.assertEquals(ITaskTemplate, schema)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplate')
        factory = fti.factory
        new_object = createObject(factory)

        self.failUnless(ITaskTemplate.providedBy(new_object))

    def test_workflow_installed(self):
        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')

        self.assertTrue('opengever_tasktemplate_workflow' in workflow)

    def test_workflows_mapped(self):
        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')

        self.assertTrue(
            'opengever_tasktemplate_workflow' in workflow.getWorkflowsFor(
                'opengever.tasktemplates.tasktemplate')[0].getId())

class TestTaskTemplatesWithBrowser(FunctionalTestCase):
    use_browser = True

    def test_view(self):
        portal = self.layer['portal']

        self.grant('Manager')

        # Folders and templates
        template_folder_1 = create_testobject(
            portal,
            'opengever.tasktemplates.tasktemplatefolder',
            title='TaskTemplateFolder 1')

        template1 = create_testobject(
            template_folder_1,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 1',
            text='Test Text',
            preselected=True,
            task_type='unidirectional_by_value',
            issuer='responsible',
            responsible_client='interactive_users',
            deadline=7,
            responsible='current_user', )
        transaction.commit()

        self.browser.open('%s' % template1.absolute_url())
        heading = self.browser.locate(".documentFirstHeading")
        self.assertEquals('TaskTemplate 1', heading.plain_text())
