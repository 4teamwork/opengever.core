from opengever.tasktemplates.content.templatefoldersschema \
    import ITaskTemplateFolderSchema
from opengever.tasktemplates.testing \
    import OPENGEVER_TASKTEMPLATES_FUNCTIONAL_TESTING
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent, addContentToContainer
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
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


class TestTaskTemplates(unittest.TestCase):

    layer = OPENGEVER_TASKTEMPLATES_FUNCTIONAL_TESTING

    def test_adding(self):
        parent = self.layer['portal']

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

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='opengever.tasktemplates.tasktemplatefolder')
        schema = fti.lookupSchema()

        self.assertEquals(ITaskTemplateFolderSchema, schema)

    def test_factory(self):

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

    def test_workflows_mapped(self):
        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')

        self.assertTrue(
            'opengever_tasktemplatefolder_workflow' in \
                workflow.getWorkflowsFor(
                    'opengever.tasktemplates.tasktemplatefolder')[0].getId())
