from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestFolderDeleteConfirmation(FunctionalTestCase):

    def setUp(self):
        super(TestFolderDeleteConfirmation, self).setUp()
        self.templatefolder = create(Builder('templatefolder'))

    def get_path(self, obj):
        return '/'.join(obj.getPhysicalPath())

    @browsing
    def test_show_portal_message_if_no_objects_where_selected(self, browser):
        browser.login().visit(self.templatefolder, view="folder_delete_confirmation")
        statusmessages.assert_message('Please select one or more items to delete.')

    @browsing
    def test_show_portal_message_if_non_existing_objects_where_selected(self, browser):
        browser.login().visit(self.templatefolder,
                              view="folder_delete_confirmation?paths:list=/not/existing")
        statusmessages.assert_message('Please select one or more items to delete.')

    @browsing
    def test_redirect_to_origin_template_if_no_objects_where_selected(self, browser):
        browser.login().visit(self.templatefolder, view="folder_delete_confirmation")

        self.assertEqual(self.templatefolder.absolute_url(),
                         browser.url)

    @browsing
    def test_list_items_to_delete_on_confirmation_form(self, browser):
        dossiertemplate = create(Builder('dossiertemplate').within(self.templatefolder))

        browser.login().visit(self.templatefolder,
                              view="folder_delete_confirmation",
                              data={'paths:list': [self.get_path(dossiertemplate)]})

        self.assertEqual([dossiertemplate.pretty_title_or_id()],
                         browser.css('#items-to-delete li').text)

    @browsing
    def test_confirmation_form_shows_a_warning_if_some_items_have_backrefs(self, browser):
        dossiertemplate = create(Builder('dossiertemplate').within(self.templatefolder))

        repo_root = create(Builder('repository_root'))
        leaf_node = create(Builder('repository')
                           .having(addable_dossier_templates=[dossiertemplate])
                           .within(repo_root))

        browser.login().visit(self.templatefolder,
                              view="folder_delete_confirmation",
                              data={'paths:list': [self.get_path(dossiertemplate)]})

        self.assertEqual([leaf_node.pretty_title_or_id()],
                         browser.css('#items-with-backlinks li').text)

    @browsing
    def test_delete_only_items_without_backrefs(self, browser):
        dossietemplate_without_backref = create(Builder('dossiertemplate').within(self.templatefolder))
        dossiertemplate_with_backref = create(Builder('dossiertemplate').within(self.templatefolder))

        repo_root = create(Builder('repository_root'))
        leaf_node = create(Builder('repository')
                           .having(addable_dossier_templates=[dossiertemplate_with_backref])
                           .within(repo_root))

        browser.login().visit(self.templatefolder,
                              view="folder_delete_confirmation",
                              data={'paths:list': [self.get_path(dossietemplate_without_backref),
                                                   self.get_path(dossiertemplate_with_backref)]})

        self.assertEqual([dossietemplate_without_backref.pretty_title_or_id()],
                         browser.css('#items-to-delete li').text)

        self.assertEqual([leaf_node.pretty_title_or_id()],
                         browser.css('#items-with-backlinks li').text)

        browser.css('form#folder_delete_confirmation').first.submit()

        statusmessages.assert_message('Items successfully deleted.')
        self.assertEqual([dossiertemplate_with_backref], self.templatefolder.listFolderContents())
        self.assertEqual(self.templatefolder.absolute_url(),
                         browser.url)
