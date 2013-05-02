from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
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
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


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

    def test_view(self):

        portal = self.layer['portal']

        # Set client-name in registry
        getUtility(IRegistry).forInterface(
            IClientConfiguration).client_id = u'plone'

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
        browser = self.get_browser()
        browser.open('%s' % template1.absolute_url())

        # Check the content
        self.assertTrue('TaskTemplate 1' in browser.contents)

    def get_browser(self):
        """Return logged in browser
        """
        # Create browser an login
        portal_url = self.layer['portal'].absolute_url()
        browser = Browser(self.layer['app'])
        browser.open('%s/login_form' % portal_url)
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()

        # Check login
        self.assertNotEquals('__ac_name' in browser.contents, True)
        self.assertNotEquals('__ac_password' in browser.contents, True)

        return browser
