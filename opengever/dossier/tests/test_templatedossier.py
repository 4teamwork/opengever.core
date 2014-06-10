from datetime import datetime, date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from opengever.dossier.templatedossier.interfaces import ITemplateUtility
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility


class TestDocumentWithTemplateForm(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    use_browser = True

    def setUp(self):
        super(TestDocumentWithTemplateForm, self).setUp()
        self.grant('Manager')

        self.modification_date = datetime(2012, 12, 28)

        self.templatedossier = create(Builder('templatedossier'))
        self.template_a = create(Builder('document')
                                 .titled('Template A')
                                 .within(self.templatedossier)
                                 .with_modification_date(self.modification_date))
        self.template_b = create(Builder('document')
                                 .titled('Template B')
                                 .within(self.templatedossier)
                                 .with_dummy_content()
                                 .with_modification_date(self.modification_date))
        self.dossier = create(Builder('dossier'))

        self.template_b_path = '/'.join(self.template_b.getPhysicalPath())

    @browsing
    def test_form_list_all_templates(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        self.assertEquals(
            [{'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'title': 'Template A'},

             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'title': 'Template B'}],
            browser.css('table.listing').first.dicts())

    @browsing
    def test_template_list_includes_nested_templates(self, browser):

        subtemplatedossier = create(Builder('templatedossier')
                                    .within(self.templatedossier))
        template_c = create(Builder('document')
                            .titled('Template C')
                            .within(subtemplatedossier)
                            .with_modification_date(self.modification_date))

        browser.login().open(self.dossier, view='document_with_template')

        self.assertEquals(
            [{'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'title': 'Template A'},
             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'title': 'Template B'},
             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'title': 'Template C'}],

            browser.css('table.listing').first.dicts())

    @browsing
    def test_template_titles_are_linked(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.find('Template B').click()
        self.assertEquals(self.template_b, browser.context)

    @browsing
    def test_cancel_redirects_to_the_dossier(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.find('Cancel').click()
        self.assertEquals(self.dossier, browser.context)
        self.assertEquals('tabbed_view', plone.view())

    @browsing
    def test_save_redirects_to_the_dossiers_document_tab(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'paths:list': self.template_b_path,
                      'title': 'Test Document'}).save()
        self.assertEquals(self.dossier, browser.context)
        self.assertEquals(self.dossier.absolute_url() + '#documents',
                          browser.url)

    @browsing
    def test_new_document_is_titled_with_the_form_value(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'paths:list': self.template_b_path,
                      'title': 'Test Document'}).save()

        document = self.dossier.listFolderContents()[0]

        self.assertEquals('Test Document', document.title)

    @browsing
    def test_new_document_values_are_filled_with_default_values(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'paths:list': self.template_b_path,
                      'title': 'Test Document'}).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(date.today(), document.document_date)
        self.assertEquals(u'privacy_layer_no', document.privacy_layer)

    @browsing
    def test_file_of_the_new_document_is_a_copy_of_the_template(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'paths:list': self.template_b_path,
                      'title': 'Test Document'}).save()

        document = self.dossier.listFolderContents()[0]

        self.assertEquals(self.template_b.file.data, document.file.data)
        self.assertNotEquals(self.template_b.file, document.file)

    # the session data manager storage is not easy availabe in the test
    #
    # @browsing
    # def test_start_external_editing_by_default(self, browser):
    #     browser.login().open(self.dossier, view='document_with_template')
    #     browser.fill({'paths:list': self.template_b_path,
    #                   'title': 'Test Document'}).save()

class TestTemplateDossier(FunctionalTestCase):

    def setUp(self):
        super(TestTemplateDossier, self).setUp()
        client1 = create_client()
        create_ogds_user(TEST_USER_ID, assigned_client=[client1])
        set_current_client_id(self.portal)

        self.grant('Manager')

    @browsing
    def test_adding(self, browser):
        browser.login().open(self.portal)
        factoriesmenu.add('Template Dossier')
        browser.fill({'Title': 'Templates',
                      'Responsible': TEST_USER_ID}).save()

        self.assertEquals('tabbed_view', plone.view())

    @browsing
    def test_addable_types(self, browser):
        templatedossier = create(Builder('templatedossier'))
        browser.login().open(templatedossier)

        self.assertEquals(
            ['Document', 'TaskTemplateFolder', 'Template Dossier'],
            factoriesmenu.addable_types())


class TestTemplateFolderUtility(FunctionalTestCase):

    def setUp(self):
        super(TestTemplateFolderUtility, self).setUp()
        self.utility = getUtility(ITemplateUtility, 'opengever.templatedossier')
        self.grant('Manager')

    def test_get_template_folder_returns_path_of_the_templatedossier(self):
        templatedossier = create(Builder('templatedossier'))

        self.assertEquals(
            '/'.join(templatedossier.getPhysicalPath()),
            self.utility.templateFolder(self.portal))

    def test_get_template_folder_returns_allways_root_templatefolder(self):
        templatedossier = create(Builder('templatedossier'))
        sub_templatefolder = create(Builder('templatedossier')
                                    .within(templatedossier))

        self.assertEquals(
            '/'.join(templatedossier.getPhysicalPath()),
            self.utility.templateFolder(self.portal))


DOCUMENT_TAB = 'tabbedview_view-documents'
TRASH_TAB = 'tabbedview_view-trash'


class TestTemplateDossierListings(FunctionalTestCase):

    def setUp(self):
        super(TestTemplateDossierListings, self).setUp()
        self.grant('Manager')

        self.templatedossier = create(Builder('templatedossier'))
        self.dossier = create(Builder('dossier'))

    def test_receipt_delivery_and_subdossier_column_are_hidden_in_document_tab(self):
        view = self.templatedossier.unrestrictedTraverse(DOCUMENT_TAB)
        view.update()
        columns = [col.get('column') for col in view.columns]

        self.assertEquals(
            ['', 'sequence_number', 'Title',
             'document_author', 'document_date', 'checked_out'],
            columns)

    def test_receipt_delivery_and_subdossier_column_are_hidden_in_trash_tab(self):
        view = self.templatedossier.unrestrictedTraverse(TRASH_TAB)
        view.update()
        columns = [col.get('column') for col in view.columns]

        self.assertEquals(
            ['', 'sequence_number', 'Title', 'document_author', 'document_date'],
            columns)

    def test_enabled_actions_are_limited_in_document_tab(self):
        view = self.templatedossier.unrestrictedTraverse(DOCUMENT_TAB)
        self.assertEquals(['trashed', 'copy_items', 'zip_selected'],
                          view.enabled_actions)

    def test_document_tab_lists_only_documents_directly_beneath(self):
        subdossier = create(Builder('templatedossier')
                            .within(self.templatedossier))
        document_a = create(Builder('document').within(self.templatedossier))
        create(Builder('document').within(subdossier))

        view = self.templatedossier.unrestrictedTraverse(DOCUMENT_TAB)
        view.update()

        self.assertEquals([document_a],
                          [brain.getObject() for brain in view.contents])

    def test_trash_tab_lists_only_documents_directly_beneath(self):
        subdossier = create(Builder('templatedossier')
                            .within(self.templatedossier))
        document_a = create(Builder('document')
                            .trashed()
                            .within(self.templatedossier))
        create(Builder('document').trashed().within(subdossier))

        view = self.templatedossier.unrestrictedTraverse(TRASH_TAB)
        view.update()

        self.assertEquals([document_a],
                          [brain.getObject() for brain in view.contents])
