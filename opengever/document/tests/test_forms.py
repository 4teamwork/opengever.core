from ftw.testbrowser import browsing
from ftw.testbrowser.widgets.file import DexterityFileWidget
from opengever.testing import IntegrationTestCase


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
