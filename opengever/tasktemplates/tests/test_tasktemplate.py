from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
from zope.component import queryUtility


class TestTaskTemplates(FunctionalTestCase):

    def test_adding(self):
        tasktemplate = create(Builder('tasktemplate')
                              .titled(u'TaskTemplate 1'))
        self.failUnless(ITaskTemplate.providedBy(tasktemplate))

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

    @browsing
    def test_view(self, browser):
        self.grant('Manager')

        # Folders and templates
        template_folder = create(Builder('tasktemplatefolder')
                                 .titled(u'TaskTemplateFolder 1'))

        template = create(Builder('tasktemplate')
                          .within(template_folder)
                          .titled(u'TaskTemplate 1')
                          .having(text=u'Test Text',
                                  preselected=True,
                                  task_type='unidirectional_by_value',
                                  issuer='responsible',
                                  responsible_client='interactive_users',
                                  deadline=7,
                                  responsible='current_user'))

        browser.login().open(template)
        self.assertEquals(['TaskTemplate 1'],
                          browser.css('.documentFirstHeading').text)

    @browsing
    def test_tasktemplatefolder_can_be_edited_when_activated(self, browser):
        templatefolder = create(Builder('tasktemplatefolder')
                                .titled(u'Task templates')
                                .in_state('tasktemplatefolder-state-activ'))

        browser.login().visit(templatefolder, view='@@edit')
        browser.find_button_by_label('Save').click()
        self.assertEquals(templatefolder.absolute_url(), browser.url)


class TestTaskTemplatesIntegration(IntegrationTestCase):

    @browsing
    def test_adding_a_tasktemplate(self, browser):
        self.login(self.administrator, browser=browser)

        templatefolder = create(Builder('tasktemplatefolder')
                                .within(self.templates)
                                .titled(u'Verfahren Neuanstellung'))

        browser.open(templatefolder)
        factoriesmenu.add('TaskTemplate')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task Type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('fa:robert.ziegler')
        form.find_widget('Issuer').fill(u'responsible')

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())

        tasktemplate = templatefolder.listFolderContents()[0]
        self.assertEquals(u'Arbeitsplatz einrichten.', tasktemplate.title)
        self.assertEquals(u'robert.ziegler', tasktemplate.responsible)
        self.assertEquals('fa', tasktemplate.responsible_client)
        self.assertEquals(u'responsible', tasktemplate.issuer)
        self.assertEquals(10, tasktemplate.deadline)
