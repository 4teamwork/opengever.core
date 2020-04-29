from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase


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
        factoriesmenu.add('RepositoryFolder')
        browser.fill({'Title': u'Sub repository'}).save()

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
                      'Task Type': 'direct-execution'})
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
