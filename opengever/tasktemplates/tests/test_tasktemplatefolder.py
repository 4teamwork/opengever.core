from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser import InsufficientPrivileges
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.tasktemplates.browser.tasktemplates import TaskTemplatesCatalogTableSource
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api


class TestTaskTemplateFolder(IntegrationTestCase):

    @browsing
    def test_adding(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.templates)
        factoriesmenu.add(u'TaskTemplateFolder')
        browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Baugesuch'], browser.css('h1').text)
        self.assertEquals('opengever.tasktemplates.tasktemplatefolder',
                          browser.context.portal_type)

    def test_default_state_is_inactive(self):
        self.login(self.administrator)
        tasktemplatefolder = create(Builder('tasktemplatefolder')
                                    .titled(u'Verfahren Neuanstellung')
                                    .within(self.templates))

        self.assertEquals('tasktemplatefolder-state-inactiv',
                          api.content.get_state(tasktemplatefolder))

    @browsing
    def test_deletion_is_possible_for_administrator(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.templates, view='folder_delete_confirmation',
                     data=self.make_path_param(self.tasktemplatefolder))
        browser.click_on('Delete')

        self.assertEquals(['Items successfully deleted.'], info_messages())
        with self.assertRaises(KeyError):
            self.tasktemplatefolder

    @browsing
    def test_deletion_is_possible_for_editor(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.templates, view='folder_delete_confirmation',
                     data=self.make_path_param(self.tasktemplatefolder))
        browser.click_on('Delete')

        self.assertEquals(['Items successfully deleted.'], info_messages())
        with self.assertRaises(KeyError):
            self.tasktemplatefolder

    @browsing
    def test_deletion_is_not_possible_for_reader(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.assertRaises(InsufficientPrivileges):
            browser.open(self.templates, view='folder_delete_confirmation',
                         data=self.make_path_param(self.tasktemplatefolder))
            browser.click_on('Delete')


class TaskTemplatesOrderingInTabbedView(SolrIntegrationTestCase):

    def test_tasks_are_sorted_by_position_in_parent(self):
        self.login(self.regular_user)

        # Create an other task template in addition of the existing `self.tasktemplate`
        # so we can play around with their position in the container.
        task_create_user = create(Builder('tasktemplate')
                                  .titled(u'Benutzer erstellen.')
                                  .having(id='task-create-user',
                                          issuer='responsible',
                                          responsible_client='fa',
                                          responsible='robert.ziegler',
                                          deadline=10)
                                  .within(self.tasktemplatefolder))

        # Commit to Solr otherwise Solr does not know about the new task template.
        self.commit_solr()

        # The new task template has been added at the bottom within the container.
        self.assertEquals(
            [
                'opengever-tasktemplates-tasktemplate',
                'task-create-user',
            ],
            self.tasktemplatefolder.objectIds()
        )

        # Move the new task template to the top within the container.
        self.tasktemplatefolder.moveObjectsToTop(task_create_user.id)

        # Make sure the change of position worked in Plone.
        self.assertEquals(
            [
                'task-create-user',
                'opengever-tasktemplates-tasktemplate',
            ],
            self.tasktemplatefolder.objectIds()
        )

        # Now get the items as the tabbed view would do.
        tabbed_view = api.content.get_view(
            name='tabbedview_view-tasktemplates',
            context=self.tasktemplatefolder,
            request=self.request
        )
        self.assertTrue(
            isinstance(tabbed_view.table_source, TaskTemplatesCatalogTableSource)
        )
        search_results = tabbed_view.table_source.search_results({
            'path': {'query': '/'.join(self.tasktemplatefolder.getPhysicalPath()), 'depth': -1},
            'portal_type': ['opengever.tasktemplates.tasktemplate'],
            'sort_on': 'getObjPositionInParent',
        })

        # Make sure the items are sorted.
        self.assertEquals(
            [
                'task-create-user',
                'opengever-tasktemplates-tasktemplate',
            ],
            [solr_doc['id'] for solr_doc in search_results.docs]
        )
