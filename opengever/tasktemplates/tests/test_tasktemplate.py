from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.testing \
    import OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING
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


class TestTaskTemplatesIntegration(unittest.TestCase):

    layer = OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING

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
