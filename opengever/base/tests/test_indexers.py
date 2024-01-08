from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
import json


class TestHasSameTypeChildren(IntegrationTestCase):

    def move_items(self, items, source=None, target=None):
        paths = u";;".join(["/".join(i.getPhysicalPath()) for i in items])
        self.request['paths'] = paths
        self.request['form.widgets.request_paths'] = paths
        self.request['form.widgets.destination_folder'] = "/".join(
            target.getPhysicalPath())

        view = source.restrictedTraverse('move_items')
        form = view.form(source, self.request)
        form.updateWidgets()
        form.widgets['destination_folder'].value = target
        form.widgets['request_paths'].value = paths

        form.handle_submit(form, object)

    def test_has_sametype_children_for_businesscasedossier(self):
        self.login(self.regular_user)

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.dossier)
        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.subdossier)
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.subsubdossier)

    def test_has_sametype_children_for_repofolders(self):
        self.login(self.regular_user)

        # Repofolder does not have the same type as reporoot
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.repository_root)
        # branch_repofolder has leaf_repofolder as child
        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.branch_repofolder)
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.leaf_repofolder)

    def test_has_sametype_children_for_tasks(self):
        self.login(self.regular_user)

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.task)
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.subtask)

    def test_has_sametype_children_for_workspaces(self):
        self.login(self.workspace_member)

        # workspace_root does not have the same type as workspace
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.workspace_root)
        # workspace does not have the same type as workspace_folder
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.workspace)
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.workspace_folder)

    def test_has_sametype_children_for_private_folder(self):
        self.login(self.regular_user)

        # private_root does not have the same type as private_folder
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.private_root)
        # private_folder does not have the same type as private_dossier
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.private_folder)
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.private_dossier)

    @browsing
    def test_is_updated_when_adding_subdossier(self, browser):
        self.login(self.regular_user, browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_dossier)

        browser.open(self.empty_dossier)
        factoriesmenu.add('Subdossier')
        browser.fill({'Title': u'Subossier'}).save()

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.empty_dossier)

    @browsing
    def test_is_updated_when_adding_repofolder(self, browser):
        self.login(self.manager, browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_repofolder)

        browser.open(self.empty_repofolder)
        factoriesmenu.add('Repository Folder')
        browser.fill({'Title (German)': u'Sub repository',
                      'Title (English)': u'Sub repository'}).save()

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.empty_repofolder)

    @browsing
    def test_is_updated_when_adding_task(self, browser):
        self.login(self.manager, browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.inbox_task)

        browser.open(self.inbox_task)
        factoriesmenu.add('Subtask')
        browser.fill({'Title': 'Subtask',
                      'Task type': 'direct-execution'})
        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.regular_user.id)
        form.find_widget('Responsible').fill(self.regular_user)
        browser.click_on('Save')

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.inbox_task)

    @browsing
    def test_is_updated_when_pasting_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_dossier)

        browser.open(self.subsubdossier, view='copy_item')
        browser.open(self.empty_dossier, view='tabbed_view')
        browser.css('#contentActionMenus a#paste').first.click()

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.empty_dossier)

    @browsing
    def test_is_updated_when_pasting_repofolder(self, browser):
        self.login(self.manager, browser=browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_repofolder)

        browser.open(self.empty_repofolder, view='copy_item')
        browser.open(self.empty_repofolder, view='tabbed_view')
        browser.css('#contentActionMenus a#paste').first.click()

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.empty_repofolder)

    @browsing
    def test_is_updated_when_moving_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_dossier)
        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.subdossier)

        self.move_items([self.subsubdossier],
                        source=self.subdossier,
                        target=self.empty_dossier)

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.empty_dossier)
        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.subdossier)

    @browsing
    def test_is_updated_when_moving_repofolder(self, browser):
        self.login(self.manager, browser=browser)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_repofolder)

        with self.observe_children(self.empty_repofolder) as children:
            self.move_items([self.inactive_repofolder],
                            source=self.repository_root,
                            target=self.empty_repofolder)

        self.assert_metadata_value(True, 'has_sametype_children',
                                   self.empty_repofolder)
        self.assertEqual(1, len(children['added']))
        inactive_repofolder = children['added'].pop()

        self.move_items([inactive_repofolder],
                        source=self.empty_repofolder,
                        target=self.branch_repofolder)

        self.assert_metadata_value(False, 'has_sametype_children',
                                   self.empty_repofolder)


class TestIsSubdossierIndexer(IntegrationTestCase):

    def test_is_subdossier_for_dossier(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier', self.dossier)
        self.assert_metadata_value(False, 'is_subdossier', self.dossier)

    def test_is_subdossier_for_meetingdossier(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier', self.meeting_dossier)
        self.assert_metadata_value(False, 'is_subdossier', self.meeting_dossier)

    def test_is_subdossier_for_subdossiers(self):
        self.login(self.regular_user)

        self.assert_index_value(True, 'is_subdossier', self.subdossier)
        self.assert_metadata_value(True, 'is_subdossier', self.subdossier)
        self.assert_index_value(True, 'is_subdossier', self.subsubdossier)
        self.assert_metadata_value(True, 'is_subdossier', self.subsubdossier)

    def test_is_subdossier_for_dossiertemplate(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier',
                                self.dossiertemplate)
        self.assert_metadata_value(False, 'is_subdossier',
                                   self.dossiertemplate)

    def test_is_subdossier_for_subdossiertemplate(self):
        self.login(self.regular_user)

        self.assert_index_value(True, 'is_subdossier',
                                self.subdossiertemplate)
        self.assert_metadata_value(True, 'is_subdossier',
                                   self.subdossiertemplate)

    def test_is_subdossier_for_reporoot(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier',
                                self.repository_root)
        self.assert_metadata_value(None, 'is_subdossier',
                                   self.repository_root)

    def test_is_subdossier_for_repofolders(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier',
                                self.branch_repofolder)
        self.assert_metadata_value(None, 'is_subdossier',
                                   self.branch_repofolder)
        self.assert_index_value(False, 'is_subdossier',
                                self.leaf_repofolder)
        self.assert_metadata_value(None, 'is_subdossier',
                                   self.leaf_repofolder)

    def test_is_subdossier_for_tasks(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier', self.task)
        self.assert_metadata_value(None, 'is_subdossier', self.task)
        self.assert_index_value(False, 'is_subdossier', self.subtask)
        self.assert_metadata_value(None, 'is_subdossier', self.subtask)

    def test_is_subdossier_for_workspaces(self):
        self.login(self.workspace_member)

        self.assert_index_value(False, 'is_subdossier', self.workspace_root)
        self.assert_metadata_value(None, 'is_subdossier', self.workspace_root)
        self.assert_index_value(False, 'is_subdossier', self.workspace)
        self.assert_metadata_value(None, 'is_subdossier', self.workspace)
        self.assert_index_value(False, 'is_subdossier', self.workspace_folder)
        self.assert_metadata_value(None, 'is_subdossier', self.workspace_folder)

    def test_is_subdossier_for_private_folder(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier', self.private_root)
        self.assert_metadata_value(None, 'is_subdossier', self.private_root)

        self.assert_index_value(False, 'is_subdossier', self.private_folder)
        self.assert_metadata_value(None, 'is_subdossier', self.private_folder)

    def test_is_subdossier_for_private_dossier(self):
        self.login(self.regular_user)

        self.assert_index_value(False, 'is_subdossier',
                                self.private_dossier)
        self.assert_metadata_value(False, 'is_subdossier',
                                   self.private_dossier)


class TestGetObjPositionInParentIndexer(SolrIntegrationTestCase):

    @browsing
    def test_index_only_for_whitelisted_types(self, browser):
        self.login(self.administrator, browser=browser)

        for obj in [self.dossier, self.proposal,
                    self.leaf_repofolder, self.task, self.workspace,
                    self.tasktemplatefolder]:
            self.assertIsNone(solr_data_for(obj, 'getObjPositionInParent'))

        self.assertEqual(0, solr_data_for(self.document,
                                          'getObjPositionInParent'))
        self.assertEqual(1, solr_data_for(self.seq_subtask_2,
                                          'getObjPositionInParent'))
        self.assertEqual(0, solr_data_for(self.tasktemplate,
                                          'getObjPositionInParent'))
        self.assertEqual(0, solr_data_for(self.workspace_meeting_agenda_item,
                                          'getObjPositionInParent'))
        self.assertEqual(6, solr_data_for(self.todo,
                                          'getObjPositionInParent'))
        self.assertEqual(4, solr_data_for(self.todolist_general,
                                          'getObjPositionInParent'))

    @browsing
    def test_get_obj_position_in_parent_if_sequential_subtask_is_added(self, browser):
        self.login(self.administrator, browser=browser)

        url = '{}/@solrsearch?sort=getObjPositionInParent asc&fl=Title,UID,getObjPositionInParent'\
              '&depth=1'.format(self.sequential_task.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.maxDiff = None

        self.assertEqual([
            (self.seq_subtask_1.Title(), 0),
            (self.seq_subtask_2.Title(), 1),
            (self.seq_subtask_3.Title(), 2)],
            [(item['Title'], item['getObjPositionInParent']) for item in browser.json["items"]])

        data = {
            '@type': 'opengever.task.task',
            'title': 'Neue Aufgabe',
            'task_type': 'direct-execution',
            'position': 2,
            'responsible': 'fa:{}'.format(self.secretariat_user.id),
            'issuer': self.regular_user.id,
        }

        browser.open(self.sequential_task, json.dumps(data),
                     method="POST", headers=self.api_headers)
        self.commit_solr()

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual([
            (self.seq_subtask_1.Title(), 0),
            (self.seq_subtask_2.Title(), 1),
            (u'Neue Aufgabe', 2), (self.seq_subtask_3.Title(), 3)],
            [(item['Title'], item['getObjPositionInParent']) for item in browser.json["items"]])

    @browsing
    def test_get_obj_position_in_parent_for_sub_tasktemplatefolder(self, browser):
        self.login(self.administrator, browser=browser)
        self.activate_feature('tasktemplatefolder_nesting')

        browser.open(self.tasktemplatefolder)
        with self.observe_children(self.tasktemplatefolder) as children:
            factoriesmenu.add(u'Task Template Folder')
            browser.fill({'Title': 'Baugesuch', 'Type': 'parallel'}).submit()

        self.commit_solr()

        self.assertEqual(1, len(children['added']))
        sub_tasktemplatefolders = children['added'].pop()
        self.assertEqual(
            1, solr_data_for(sub_tasktemplatefolders, 'getObjPositionInParent'))
        self.assertEqual(
            0, solr_data_for(self.tasktemplate, 'getObjPositionInParent'))


class TestIsFolderishIndexer(SolrIntegrationTestCase):

    @browsing
    def test_is_folderish_solr_index(self, browser):
        self.login(self.administrator, browser=browser)

        url = u'{}/@solrsearch?sort=portal_type asc&fl=is_folderish&fq=UID:({})'.format(
            self.portal.absolute_url(),
            ' OR '.join([
                self.leaf_repofolder.UID(),
                self.dossier.UID(),
                self.document.UID(),
                self.task.UID(),
                self.seq_subtask_2.UID(),
                self.proposal.UID(),
                self.tasktemplate.UID(),
                self.workspace.UID(),
                self.todolist_general.UID(),
                self.todo.UID(),
            ]))
        browser.open(url, method='GET', headers=self.api_headers)
        self.maxDiff = None

        self.assertEqual([
            {u'UID': self.document.UID(),
             u'is_folderish': False},
            {u'UID': self.dossier.UID(),
             u'is_folderish': True},
            {u'UID': self.proposal.UID(),
             u'is_folderish': True},
            {u'UID': self.leaf_repofolder.UID(),
             u'is_folderish': True},
            {u'UID': self.task.UID(),
             u'is_folderish': True},
            {u'UID': self.seq_subtask_2.UID(),
             u'is_folderish': True},
            {u'UID': self.tasktemplate.UID(),
             u'is_folderish': False},
            {u'UID': self.todo.UID(),
             u'is_folderish': True},
            {u'UID': self.todolist_general.UID(),
             u'is_folderish': True},
            {u'UID': self.workspace.UID(),
             u'is_folderish': True}
        ], browser.json["items"])
