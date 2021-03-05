from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.widgets.file import DexterityFileWidget
from opengever.testing import IntegrationTestCase
from requests_toolbelt.utils import formdata


class TestDocumentIntegration(IntegrationTestCase):
    """Test document forms."""

    @browsing
    def test_edit_form_document_not_checked_out(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='edit')
        self.assertEqual(
            u'Vertraegsentwurf.docx \u2014 26 KB',
            browser.css('.named-file-widget.namedblobfile-field').first.text,
        )
        # Edit should not be posssible
        self.assertEqual([], browser.css('#form-widgets-file label').text)
        # Save should not adjust the file
        browser.fill({'Title': 'foo'})
        browser.find('Save').click()
        self.assertTrue(self.document.file)

    @browsing
    def test_edit_form_document_is_checked_out(self, browser):
        self.login(self.regular_user, browser)
        # Checkout the document
        self.get_checkout_manager(self.document).checkout()
        browser.open(self.document, view='edit')
        expected_url = '{}/file_download_confirmation'.format(self.document.absolute_url())
        self.assertEqual(expected_url, browser.css('#form-widgets-file a.link-overlay').first.get('href'))
        # Edit should be posssible
        expected_file_actions = ['Keep existing file', 'Remove existing file', 'Replace with new file']
        self.assertEqual(expected_file_actions, browser.css('#form-widgets-file label').text)

    @browsing
    def test_edit_form_without_document_shows_file_input_field(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_document, view='edit')
        file_field = browser.forms.get('form').find_field('File')
        self.assertIsNotNone(file_field)
        self.assertTrue(isinstance(file_field, DexterityFileWidget))

    @browsing
    def test_edit_form_does_not_contain_change_note(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='edit')
        inputs = [form_input.name for form_input in browser.forms.get('form').inputs]
        self.assertNotIn('form.widgets.IVersionable.changeNote', inputs)

    @browsing
    def test_add_form_does_not_contain_change_note(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='++add++opengever.document.document')
        inputs = [form_input.name for form_input in browser.forms.get('form').inputs]
        self.assertNotIn('form.widgets.IVersionable.changeNote', inputs)

    @browsing
    def test_add_form_does_not_list_shadow_documents_as_relatable(self, browser):
        """Dossier responsible has created the shadow document.

        This test ensures he does not get it offered as a relatable document on
        documents.
        """
        self.login(self.dossier_responsible, browser)
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '++add++opengever.document.document',
            '++widget++form.widgets.IRelatedDocuments.relatedItems',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
        )
        expected_documents = [
            '2015',
            '2016',
            '[No Subject]',
            u'Die B\xfcrgschaft',
            u'Initialvertrag f\xfcr Bearbeitung',
            u'Vertr\xe4gsentwurf',
        ]
        self.assertEqual(expected_documents, browser.css('li').text)

    @browsing
    def test_add_form_resets_file_when_validation_fails(self, browser):
        self.login(self.manager, browser)

        choices = ["one", "two", "three"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
        )

        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Document')
        browser.fill({'Title': u'My Document',
                      'File': ('DATA', 'file.txt', 'text/plain'),
                      "Document type": "Inquiry"}).save()

        # the initial save will produce errors as we now have a document_type
        # which requires some mandatory custom properties.
        self.assertEqual(["There were some errors."], error_messages())

        # We want to make sure that the NamedFileWidget was reset
        # and does not display an already uploaded file that will
        # actually not be set
        form = browser.find_form_by_field('File')
        widget = form.find_widget('File')
        self.assertNotIn("Remove existing file", widget.text)
        self.assertEqual("File The document's digital file", widget.text)


class TestDocumentFileUploadForm(IntegrationTestCase):
    """Test document file upload forms."""

    @browsing
    def test_file_upload_form_renders_file_field(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='file_upload')
        file_field = browser.forms.get('form').find_field('File')
        self.assertIsNotNone(file_field)
        self.assertTrue(isinstance(file_field, DexterityFileWidget))

    @browsing
    def test_file_upload_form_doesnt_render_title_field(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='file_upload')
        title_field = browser.forms.get('form').find_field('Title')
        self.assertIsNone(title_field)

    @browsing
    def test_file_upload_form_replaces_file(self, browser):
        self.login(self.regular_user, browser)
        # Checkout the document
        self.get_checkout_manager(self.document).checkout()
        browser.open(self.document, view='file_upload')
        browser.fill({
            'File': ('New file data', 'file.txt', 'text/plain'),
            'form.widgets.file.action': 'replace',
            })
        browser.find('oc-file-upload').click()
        self.assertEqual('New file data', self.document.file.data)

    @browsing
    def test_file_upload_fails_if_document_isnt_checked_out(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='file_upload')
        browser.fill({
            'File': ('New file data', 'file.txt', 'text/plain'),
            'form.widgets.file.action': 'replace',
            })
        with browser.expect_http_error(code=412):
            browser.find('oc-file-upload').click()
