from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.widgets.file import DexterityFileWidget
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import IRefreshableLockable
from zope.component import queryMultiAdapter
import transaction


class TestDocumentIntegration(FunctionalTestCase):
    """Test document forms."""

    def setUp(self):
        super(TestDocumentIntegration, self).setUp()
        login(self.portal, TEST_USER_NAME)

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .having(digitally_available=True)
            .with_dummy_content())

    @browsing
    def test_edit_form_document_not_checked_out(self, browser):
        browser.login().open(self.document, view='edit')

        self.assertEqual(
            u'document1.doc \u2014 1 KB',
            browser.css('.named-file-widget.namedblobfile-field').first.text)

        # edit should not be posssible
        self.assertEqual([], browser.css('#form-widgets-file label').text)

        # save should not adjust the file
        browser.fill({'Title': 'foo'})
        browser.find('Save').click()
        self.assertTrue(self.document.file)

    @browsing
    def test_edit_form_document_is_checked_out(self, browser):
        # checkout the document
        manager = queryMultiAdapter((self.document, self.document.REQUEST),
                                    ICheckinCheckoutManager)
        manager.checkout()
        transaction.commit()

        browser.login().open(self.document, view='edit')

        self.assertEqual(
            '{}/file_download_confirmation'
            .format(self.document.absolute_url()),
            browser.css('#form-widgets-file a.link-overlay').first.get('href'))

        # edit should be posssible
        self.assertEqual(
            ['Keep existing file',
             'Remove existing file',
             'Replace with new file'],
            browser.css('#form-widgets-file label').text)

        IRefreshableLockable(self.document).unlock()
        transaction.commit()

        manager.cancel()

    @browsing
    def test_edit_form_without_document_shows_file_input_field(self, browser):
        self.document.file = None
        self.document.digitally_available = False
        transaction.commit()

        browser.login().open(self.document, view='edit')

        file_field = browser.forms.get('form').find_field('File')
        self.assertIsNotNone(file_field)
        self.assertTrue(isinstance(file_field, DexterityFileWidget))

    @browsing
    def test_edit_form_does_not_contain_change_note(self, browser):
        browser.login().open(self.document, view='edit')

        inputs = [
            form_input.name
            for form_input in browser.forms.get('form').inputs
            ]
        self.assertNotIn('form.widgets.IVersionable.changeNote', inputs)

    @browsing
    def test_add_form_does_not_contain_change_note(self, browser):
        browser.login().open(
            self.portal, view='++add++opengever.document.document')

        inputs = [
            form_input.name
            for form_input in browser.forms.get('form').inputs
            ]
        self.assertNotIn('form.widgets.IVersionable.changeNote', inputs)


class TestDocumentFileUploadForm(FunctionalTestCase):
    """Test document file upload forms."""

    def setUp(self):
        super(TestDocumentFileUploadForm, self).setUp()
        login(self.portal, TEST_USER_NAME)

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .having(digitally_available=True)
            .with_dummy_content())

    @browsing
    def test_file_upload_form_renders_file_field(self, browser):
        browser.login().open(self.document, view='file_upload')
        file_field = browser.forms.get('form').find_field('File')
        self.assertIsNotNone(file_field)
        self.assertTrue(isinstance(file_field, DexterityFileWidget))

    @browsing
    def test_file_upload_form_doesnt_render_title_field(self, browser):
        browser.login().open(self.document, view='file_upload')
        title_field = browser.forms.get('form').find_field('Title')
        self.assertIsNone(title_field)

    @browsing
    def test_file_upload_form_replaces_file(self, browser):
        # checkout the document
        manager = queryMultiAdapter((self.document, self.document.REQUEST),
                                    ICheckinCheckoutManager)
        manager.checkout()
        transaction.commit()

        browser.login().open(self.document, view='file_upload')
        browser.fill({
            'File': ('New file data', 'file.txt', 'text/plain'),
            'form.widgets.file.action': 'replace',
            })
        browser.find('oc-file-upload').click()
        self.assertEqual('New file data', self.document.file.data)

    @browsing
    def test_file_upload_fails_if_document_isnt_checked_out(self, browser):
        browser.login().open(self.document, view='file_upload')
        browser.fill({
            'File': ('New file data', 'file.txt', 'text/plain'),
            'form.widgets.file.action': 'replace',
            })
        with browser.expect_http_error(code=412):
            browser.find('oc-file-upload').click()
