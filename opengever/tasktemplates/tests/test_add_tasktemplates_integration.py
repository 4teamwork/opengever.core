from datetime import datetime, timedelta
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.content.templatefoldersschema \
    import ITaskTemplateFolderSchema
from opengever.tasktemplates.testing \
    import OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent, addContentToContainer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
import unittest2 as unittest


def create_testobject(parent, ptype, **kwargs):
    createContent(ptype)
    obj = createContent(ptype, **kwargs)
    notify(ObjectCreatedEvent(obj))
    obj = addContentToContainer(parent, obj, checkConstraints=False)
    notify(ObjectAddedEvent(obj))
    return obj


class TestTaskTemplatesIntegration(unittest.TestCase):

    layer = OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING

    def test_adding(self):
        parent = self.layer['portal']

        t1 = create_testobject(
            parent,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 1')

        self.failUnless(ITaskTemplate.providedBy(t1))

        t2 = create_testobject(
            parent,
            'opengever.tasktemplates.tasktemplatefolder',
            title='TaskTemplateFolder 1')

        self.failUnless(ITaskTemplateFolderSchema.providedBy(t2))

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplatefolder')

        self.assertNotEquals(None, fti)

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

        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplatefolder')
        schema = fti.lookupSchema()

        self.assertEquals(ITaskTemplateFolderSchema, schema)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplate')
        factory = fti.factory
        new_object = createObject(factory)

        self.failUnless(ITaskTemplate.providedBy(new_object))

        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplatefolder')
        factory = fti.factory
        new_object = createObject(factory)

        self.failUnless(ITaskTemplateFolderSchema.providedBy(new_object))

    def test_workflow_installed(self):
        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')

        self.assertTrue('opengever_tasktemplatefolder_workflow' in workflow)
        self.assertTrue('opengever_tasktemplate_workflow' in workflow)

    def test_workflows_mapped(self):
        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')

        self.assertTrue(
            'opengever_tasktemplatefolder_workflow' in \
                workflow.getWorkflowsFor(
                    'opengever.tasktemplates.tasktemplatefolder')[0].getId())
        self.assertTrue(
            'opengever_tasktemplate_workflow' in workflow.getWorkflowsFor(
                'opengever.tasktemplates.tasktemplate')[0].getId())

    def test_permissions_tasktemplate(self):
        pass

        # TODO:

        # portal = self.layer['portal']
        # workflow = getToolByName(portal, 'portal_workflow')
        #
        # template_folder = create_testobject(
        #     portal, 'opengever.tasktemplates.tasktemplatefolder', title='TaskTemplateFolder 1')
        #
        # template = create_testobject(
        #     template_folder,
        #     'opengever.tasktemplates.tasktemplate',
        #     title='TaskTemplate 1',)

    def test_permissions_tasktemplatefolder(self):
        pass

    def test_view(self):
        pass

    def test_integration(self):
        """ Tests the integration of tasktemplatefolder and
        tasktemplate
        """

        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')
        catalog = getToolByName(portal, 'portal_catalog')
        mtool = getToolByName(portal, 'portal_membership')

        # Set client-name in registry
        getUtility(IRegistry).forInterface(
            IClientConfiguration).client_id = u'plone'

        # Folders and templates
        template_folder_1 = create_testobject(
            portal,
            'opengever.tasktemplates.tasktemplatefolder',
            title='TaskTemplateFolder 1')

        template_folder_2 = create_testobject(
            portal,
            'opengever.tasktemplates.tasktemplatefolder',
            title='TaskTemplateFolder 2')

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
            responsible='current_user',)

        template2 = create_testobject(
            template_folder_1,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 2')

        # Activate folder 1
        workflow.doActionFor(template_folder_1,
                             'tasktemplatefolder-transition-inactiv-activ')

        dossier = create_testobject(
            portal,
            'opengever.dossier.businesscasedossier',
            title='Dossier 1',
        )
        IDossier(dossier).responsible = 'zopemaster'

        add_tasktemplate_view = dossier.restrictedTraverse('add-tasktemplate')

        # We just can find folder 1 because folder 2 is inactive
        self.assertTrue(
            template_folder_1.title in add_tasktemplate_view.listing(
                show='templates'))
        self.assertFalse(
            template_folder_2.title in add_tasktemplate_view.listing(
                show='templates'))

        # Activate folder 2
        workflow.doActionFor(template_folder_2,
                             'tasktemplatefolder-transition-inactiv-activ',)

        # Now we can see both
        self.assertTrue(
            template_folder_1.title in add_tasktemplate_view.listing(
                show='templates'))
        self.assertTrue(
            template_folder_2.title in add_tasktemplate_view.listing(
                show='templates'))

        # In folder 1 we can find two tasktemplates
        self.assertTrue(
            template1.title in add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_1.getPhysicalPath())))

        self.assertTrue(
            template2.title in add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_1.getPhysicalPath())))

        # In folder 2 we can't find any tasktemplates
        self.assertFalse(
            template1.title in add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_2.getPhysicalPath())))

        self.assertFalse(
            template2.title in add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_2.getPhysicalPath())))

        add_tasktemplate_view.create(
            paths=["/".join(template1.getPhysicalPath())])

        brains = catalog(
            path='/'.join(dossier.getPhysicalPath()),
                portal_type='opengever.task.task')

        # We should have now one Task-Object
        self.assertTrue(1 == len(brains))

        task = brains[0]

        # Check the attributes from the template
        self.assertTrue(task.Title == template1.title)
        self.assertTrue(
            task.responsible == mtool.getAuthenticatedMember().getId())
        self.assertTrue(
            task.deadline.date() == (datetime.today() + timedelta(
                template1.deadline)).date())
        self.assertTrue(task.getObject().text == template1.text)
        self.assertTrue(task.issuer == IDossier(dossier).responsible)
