from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser import InsufficientPrivileges
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.tasktemplates.browser.tasktemplates import TaskTemplatesCatalogTableSource
from opengever.tasktemplates.tasktemplatefolder import ACTIVE_STATE
from opengever.tasktemplates.tasktemplatefolder import INACTIVE_STATE
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.helpers import solr_data_for
from plone import api


class TestTaskTemplateFolder(IntegrationTestCase):

    @browsing
    def test_adding(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.templates)
        factoriesmenu.add(u'Task Template Folder')
        browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Baugesuch'], browser.css('h1').text)
        self.assertEquals('opengever.tasktemplates.tasktemplatefolder',
                          browser.context.portal_type)

    @browsing
    def test_adding_subtasktemplatefolder_only_possible_if_feature_is_enabled(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplatefolder)
        self.assertNotIn(u'Task Template Folder', factoriesmenu.addable_types())

        self.activate_feature('tasktemplatefolder_nesting')
        browser.open(self.tasktemplatefolder)
        self.assertIn(u'Task Template Folder', factoriesmenu.addable_types())

        factoriesmenu.add(u'Task Template Folder')
        browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.assertEqual(['Item created'], info_messages())
        self.assertEqual(['Baugesuch'], browser.css('h1').text)
        self.assertEqual('opengever.tasktemplates.tasktemplatefolder',
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

        self.assertEquals(['Items deleted successfully.'], info_messages())
        with self.assertRaises(KeyError):
            self.tasktemplatefolder

    @browsing
    def test_deletion_is_possible_for_editor(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.templates, view='folder_delete_confirmation',
                     data=self.make_path_param(self.tasktemplatefolder))
        browser.click_on('Delete')

        self.assertEquals(['Items deleted successfully.'], info_messages())
        with self.assertRaises(KeyError):
            self.tasktemplatefolder

    @browsing
    def test_deletion_is_not_possible_for_reader(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.assertRaises(InsufficientPrivileges):
            browser.open(self.templates, view='folder_delete_confirmation',
                         data=self.make_path_param(self.tasktemplatefolder))
            browser.click_on('Delete')

    @browsing
    def test_shows_warning_when_contains_sub_tasktemplatefolder(self, browser):
        self.login(self.administrator, browser=browser)
        self.activate_feature('tasktemplatefolder_nesting')

        browser.open(self.tasktemplatefolder)
        self.assertEqual([], warning_messages())

        factoriesmenu.add(u'Task Template Folder')
        browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.assertEqual(
            ['Nested TaskTemplateFolders can only be viewed and edited '
             'correctly in the new UI.'],
            warning_messages())

    @browsing
    def test_state_transitions_are_recursive(self, browser):
        self.login(self.administrator, browser=browser)
        self.activate_feature('tasktemplatefolder_nesting')
        subtasktemplatefolder = create(
            Builder('tasktemplatefolder')
            .titled(u'Verfahren Neuanstellung')
            .within(self.tasktemplatefolder)
            .in_state('tasktemplatefolder-state-activ'))

        subsubtasktemplatefolder = create(
            Builder('tasktemplatefolder')
            .titled(u'Verfahren Neuanstellung')
            .within(subtasktemplatefolder)
            .in_state('tasktemplatefolder-state-activ'))

        self.assertEqual('tasktemplatefolder-state-activ',
                         api.content.get_state(self.tasktemplatefolder))
        self.assertEqual('tasktemplatefolder-state-activ',
                         api.content.get_state(subtasktemplatefolder))
        self.assertEqual('tasktemplatefolder-state-activ',
                         api.content.get_state(subsubtasktemplatefolder))

        # Inactivate
        url = '{}/@workflow/tasktemplatefolder-transition-activ-inactiv'.format(
            self.tasktemplatefolder.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual('tasktemplatefolder-state-inactiv',
                         api.content.get_state(self.tasktemplatefolder))
        self.assertEqual('tasktemplatefolder-state-inactiv',
                         api.content.get_state(subtasktemplatefolder))
        self.assertEqual('tasktemplatefolder-state-inactiv',
                         api.content.get_state(subsubtasktemplatefolder))

        # Activate
        url = '{}/@workflow/tasktemplatefolder-transition-inactiv-activ'.format(
            self.tasktemplatefolder.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual('tasktemplatefolder-state-activ',
                         api.content.get_state(self.tasktemplatefolder))
        self.assertEqual('tasktemplatefolder-state-activ',
                         api.content.get_state(subtasktemplatefolder))
        self.assertEqual('tasktemplatefolder-state-activ',
                         api.content.get_state(subsubtasktemplatefolder))

    @browsing
    def test_cannot_activate_subtasktemplatefolder(self, browser):
        self.login(self.administrator, browser=browser)
        self.activate_feature('tasktemplatefolder_nesting')
        subtasktemplatefolder = create(
            Builder('tasktemplatefolder')
            .titled(u'Verfahren Neuanstellung')
            .within(self.tasktemplatefolder)
            .in_state('tasktemplatefolder-state-inactiv'))

        # Activate
        url = '{}/@workflow/tasktemplatefolder-transition-inactiv-activ'.format(
            subtasktemplatefolder.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            u"Invalid transition 'tasktemplatefolder-transition-inactiv-activ'."
            u"\nValid transitions are:\n",
            browser.json['error']['message']
            )

    @browsing
    def test_cannot_inactivate_subtasktemplatefolder(self, browser):
        self.login(self.administrator, browser=browser)
        self.activate_feature('tasktemplatefolder_nesting')
        subtasktemplatefolder = create(
            Builder('tasktemplatefolder')
            .titled(u'Verfahren Neuanstellung')
            .within(self.tasktemplatefolder)
            .in_state('tasktemplatefolder-state-activ'))

        # Activate
        url = '{}/@workflow/tasktemplatefolder-transition-activ-inactiv'.format(
            subtasktemplatefolder.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            u"Invalid transition 'tasktemplatefolder-transition-activ-inactiv'."
            u"\nValid transitions are:\n",
            browser.json['error']['message']
            )

    @browsing
    def test_subtasktemplatefolders_are_created_in_same_status_as_parent(self, browser):
        self.login(self.administrator, browser=browser)
        self.activate_feature('tasktemplatefolder_nesting')

        self.assertEqual(ACTIVE_STATE, api.content.get_state(self.tasktemplatefolder))

        # Add subtasktemplatefolder in active tasktemplatefolder
        browser.open(self.tasktemplatefolder)
        factoriesmenu.add(u'Task Template Folder')
        with self.observe_children(self.tasktemplatefolder) as children:
            browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.assertEqual(1, len(children["added"]))
        subtasktemplatefolder = children["added"].pop()
        self.assertEqual(ACTIVE_STATE, api.content.get_state(subtasktemplatefolder))

        # Inactivate
        url = '{}/@workflow/tasktemplatefolder-transition-activ-inactiv'.format(
            self.tasktemplatefolder.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)
        self.assertEqual(INACTIVE_STATE, api.content.get_state(self.tasktemplatefolder))

        # Add subtasktemplatefolder in inactive tasktemplatefolder
        browser.open(self.tasktemplatefolder)
        factoriesmenu.add(u'Task Template Folder')
        with self.observe_children(self.tasktemplatefolder) as children:
            browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.assertEqual(1, len(children["added"]))
        subtasktemplatefolder2 = children["added"].pop()
        self.assertEqual(INACTIVE_STATE, api.content.get_state(subtasktemplatefolder2))


class TestTaskTemplateFolderWithSolr(SolrIntegrationTestCase):

    @browsing
    def test_is_subtasktemplatefolder(self, browser):
        self.activate_feature('tasktemplatefolder_nesting')

        self.login(self.administrator, browser=browser)
        with self.observe_children(self.tasktemplatefolder) as children:
            browser.open(self.tasktemplatefolder)
            factoriesmenu.add(u'Task Template Folder')
            browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.commit_solr()

        self.assertEqual(1, len(children["added"]))
        subtasktemplatefolder = children["added"].pop()

        self.assertFalse(self.tasktemplatefolder.is_subtasktemplatefolder())
        self.assertFalse(solr_data_for(self.tasktemplatefolder).get('is_subtasktemplatefolder'))
        self.assertTrue(subtasktemplatefolder.is_subtasktemplatefolder())
        self.assertTrue(solr_data_for(subtasktemplatefolder).get('is_subtasktemplatefolder'))


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
        self.commit_solr()

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
