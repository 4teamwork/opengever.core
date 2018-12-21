from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from plone import api
import transaction


class TestFolderDeleteConfirmation(IntegrationTestCase):

    def get_path(self, obj):
        return '/'.join(obj.getPhysicalPath())

    @browsing
    def test_show_portal_message_if_no_objects_where_selected(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.templates, view="folder_delete_confirmation")

        statusmessages.assert_message('Please select one or more items to delete.')

    @browsing
    def test_show_portal_message_if_non_existing_objects_where_selected(self, browser):
        self.login(self.administrator, browser=browser)
        browser.visit(self.templates,
                      view="folder_delete_confirmation?paths:list=/not/existing")
        statusmessages.assert_message('Please select one or more items to delete.')

    @browsing
    def test_redirect_to_origin_template_if_no_objects_where_selected(self, browser):
        self.login(self.administrator, browser=browser)
        browser.visit(self.templates, view="folder_delete_confirmation")

        self.assertEqual(self.templates.absolute_url(), browser.url)

    @browsing
    def test_list_items_to_delete_on_confirmation_form(self, browser):
        self.login(self.administrator, browser=browser)
        browser.visit(self.templates,
                      view="folder_delete_confirmation",
                      data=self.make_path_param(self.dossiertemplate))

        self.assertEqual([self.dossiertemplate.pretty_title_or_id()],
                         browser.css('#items-to-delete li').text)

    @browsing
    def test_confirmation_form_shows_a_warning_if_some_items_have_backrefs(self, browser):
        self.login(self.administrator, browser=browser)
        leaf_node = create(Builder('repository')
                           .having(addable_dossier_templates=[self.dossiertemplate])
                           .within(self.repository_root))

        browser.visit(self.templates,
                      view="folder_delete_confirmation",
                      data=self.make_path_param(self.dossiertemplate))

        self.assertEqual([leaf_node.pretty_title_or_id()],
                         browser.css('#items-with-backlinks li').text)

    @browsing
    def test_delete_only_items_without_backrefs(self, browser):
        self.login(self.administrator, browser=browser)

        dossiertemplate_with_backref = create(Builder('dossiertemplate')
                                              .within(self.templates))

        leaf_node = create(Builder('repository')
                           .having(addable_dossier_templates=[dossiertemplate_with_backref])
                           .within(self.repository_root))

        browser.visit(self.templates,
                      view="folder_delete_confirmation",
                      data=self.make_path_param(self.dossiertemplate,
                                                dossiertemplate_with_backref))

        self.assertEqual([self.dossiertemplate.pretty_title_or_id()],
                         browser.css('#items-to-delete li').text)

        self.assertEqual([leaf_node.pretty_title_or_id()],
                         browser.css('#items-with-backlinks li').text)

        browser.css('form#folder_delete_confirmation').first.submit()

        statusmessages.assert_message('Items successfully deleted.')
        self.assertIn(dossiertemplate_with_backref, self.templates.objectValues())
        with self.assertRaises(KeyError):
            self.dossiertemplate

        self.assertEqual(self.templates.absolute_url(), browser.url)
