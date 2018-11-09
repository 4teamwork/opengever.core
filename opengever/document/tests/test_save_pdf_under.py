from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.base.security import elevated_privileges
from opengever.document.archival_file import STATE_CONVERTED
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.versioner import Versioner
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_STATUS_KEY
from opengever.document.browser.save_pdf_document_under import SavePDFDocumentUnder
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations


class TestSavePDFUnderForm(IntegrationTestCase):
    """Test save pdf under form."""

    features = ('bumblebee', )

    @browsing
    def test_save_pdf_under_form_renders_destination_folder_field(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')

        destination_folder_field = browser.forms.get('form').find_field("Destination")
        self.assertIsNotNone(destination_folder_field)

    @browsing
    def test_save_pdf_under_form_hides_version_id_field(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')

        version_field = browser.forms.get('form').find_field("form.widgets.version_id")
        self.assertEqual('hidden', version_field.type)

    @browsing
    def test_save_pdf_under_form_only_allows_dossier_as_destination(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')
        form_url = browser.url
        browser.forms.get('form').find_field("Destination").fill(self.leaf_repofolder)
        with self.observe_children(self.leaf_repofolder) as children:
            browser.click_on("Save")

        self.assertFalse(len(children["added"]) > 0)
        self.assertEqual(form_url, browser.url)

        error_nodes = browser.css("div.fieldErrorBox div.error")
        self.assertTrue(len(error_nodes) > 0)
        self.assertEqual("Required input is missing.",
                         error_nodes.first.text)

    @browsing
    def test_save_pdf_under_form_validates_destination_allowed_content_types(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')
        form_url = browser.url
        self.portal.portal_types["opengever.dossier.businesscasedossier"].allowed_content_types = ()
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertFalse(len(children["added"]) > 0)
        self.assertEqual(form_url, browser.url)

        error_nodes = browser.css("div.fieldErrorBox div.error")
        self.assertTrue(len(error_nodes) > 0)
        self.assertEqual("User is not allowed to add a document there.",
                         error_nodes.first.text)

    @browsing
    def test_save_pdf_under_form_validates_user_permissions_on_destination_folder(self, browser):
        self.login(self.regular_user, browser)

        with elevated_privileges():
            self.empty_dossier.__ac_local_roles_block__ = True
            self.empty_dossier.manage_setLocalRoles(self.regular_user.id, roles=['Authenticated', 'Reader'], verified=True)
        browser.open(self.document, view='save_pdf_under')
        form_url = browser.url
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertFalse(len(children["added"]) > 0)
        self.assertEqual(form_url, browser.url)

        error_nodes = browser.css("div.fieldErrorBox div.error")
        self.assertTrue(len(error_nodes) > 0)
        self.assertEqual('User is not allowed to add a document there.',
                         error_nodes.first.text)

    @browsing
    def test_save_pdf_under_form_asserts_version_is_convertable(self, browser):
        self.login(self.regular_user, browser)
        self.document.file.filename = u"test.wav"
        self.document.file.contentType = "audio/wav"
        Versioner(self.document).create_version("")

        self.document.file.filename = u"test.txt"
        self.document.file.contentType = "text/plain"
        Versioner(self.document).create_version("")

        # when the version is convertable, we get to the form
        browser.open(self.document, view='save_pdf_under', data={"version_id": "1"})
        self.assertEqual("/".join([self.document.absolute_url(), 'save_pdf_under']),
                         browser.url)

        # when the version cannot be converted, we get redirected back to the
        # the source document and an error message is displayed.
        browser.open(self.document, view='save_pdf_under', data={"version_id": "0"})
        errors = statusmessages.error_messages()
        self.assertEqual(1, len(errors))
        self.assertEqual('This document cannot be converted to PDF.', errors[0])
        self.assertEqual(self.document.absolute_url(), browser.url)

    @browsing
    def test_save_pdf_under_form_creates_empty_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()

        self.assertTrue(created_document.is_shadow_document())
        self.assertFalse(created_document.has_file())

    @browsing
    def test_save_pdf_under_form_copies_metadata_to_created_document(self, browser):
        self.login(self.regular_user, browser)

        # Fill metadata of document
        metadata_dict = {"description": "Document description",
                         u'keywords': ("test", "document"),
                         u'foreign_reference': "1234",
                         u'document_date': datetime(2018, 1, 1),
                         u'receipt_date': datetime(2018, 1, 2),
                         u'delivery_date': datetime(2018, 1, 3),
                         u'document_type': 'contract',
                         u'document_author': 'test_user_1_',
                         u'preserved_as_paper': True,
                         u'digitally_available': True,
                         u'thumbnail': "thumbnail",
                         u'preview': "preview",
                         u"archival_file": "archival_file",
                         u"archival_file_state": STATE_CONVERTED,
                         }

        # fields that should not be copied over
        fields_to_skip = set(("file", "archival_file", "archival_file_state",
                              "thumbnail", "preview", "digitally_available"))

        for field, value in metadata_dict.items():
            setattr(IDocumentMetadata(self.document), field, value)

        browser.open(self.document, view='save_pdf_under')
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()

        for field, value in metadata_dict.items():
            if field in fields_to_skip:
                self.assertNotEqual(
                    value,
                    getattr(IDocumentMetadata(created_document), field),
                    "{} should not be copied to destination document".format(field)
                    )
            else:
                self.assertEqual(
                    value,
                    getattr(IDocumentMetadata(created_document), field),
                    "{} should be copied to destination document".format(field)
                    )

    @browsing
    def test_save_pdf_under_form_sets_relation_to_source_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()

        related_items = IRelatedDocuments(created_document).relatedItems
        self.assertEqual(len(related_items), 1)
        self.assertEqual(related_items[0].to_object, self.document)

    @browsing
    def test_save_pdf_under_form_created_document_annotations(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()

        annotations = IAnnotations(created_document)
        self.assertEqual(IUUID(self.document),
                         annotations.get('opengever.document.save_pdf_under_source_uuid'))
        self.assertEqual('conversion-demanded',
                         annotations.get('opengever.document.save_pdf_under_status'))
        self.assertIsNotNone(annotations.get('opengever.document.save_pdf_under_token'))

    @browsing
    def test_save_pdf_under_form_redirects_to_demand_document_pdf(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='save_pdf_under')
        browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children:
            browser.click_on("Save")

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()

        message = u'Document {} was successfully created in {}'.format(self.document.title, self.empty_dossier.title)
        self.assertEqual(statusmessages.info_messages()[0], message)

        expected_path = "/".join([created_document.absolute_url(), 'demand_document_pdf'])
        self.assertEqual(expected_path, browser.url)


class TestSavePDFDocumentUnder(IntegrationTestCase):
    """Test the demand document PDF view."""

    features = ('bumblebee', )

    def prepare_destination_document(self, browser):
        with self.login(self.regular_user, browser), self.observe_children(self.empty_dossier) as children:
            browser.open(self.document, view='save_pdf_under')
            browser.forms.get('form').find_field("Destination").fill(self.empty_dossier)
            browser.click_on("Save")
        return children["added"].pop()

    @browsing
    def test_demand_document_pdf_view_urls(self, browser):
        created_document = self.prepare_destination_document(browser)
        self.login(self.regular_user, browser)

        view = SavePDFDocumentUnder(created_document, self.request)
        view()

        self.assertEqual(self.document.absolute_url(), view.source_document_url())

        self.assertEqual(created_document.absolute_url(), view.destination_document_url())

        expected_callback_url = "/".join([created_document.absolute_url(), "save_pdf_under_callback"])
        expected_callback_url += "?pdf_save_under_token=test_token"
        self.assertEqual(expected_callback_url, view.get_callback_url("test_token"))

    @browsing
    def test_demand_document_pdf_conversion_status_is_traversable(self, browser):
        created_document = self.prepare_destination_document(browser)
        self.login(self.regular_user, browser)

        view = SavePDFDocumentUnder(created_document, self.request)
        view()

        browser.open(view.get_conversion_status_url())
        self.assertEqual(browser.json['conversion-status'], 'conversion-demanded')

        IAnnotations(created_document)[PDF_SAVE_STATUS_KEY] = 'conversion-successful'
        browser.open(view.get_conversion_status_url())
        self.assertEqual(browser.json['conversion-status'], 'conversion-successful')
