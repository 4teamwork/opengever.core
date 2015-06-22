from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from zope.component import queryMultiAdapter
import transaction


class TestDocumentIntegration(FunctionalTestCase):
    use_browser = True

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
            '{}/file_download_confirmation'.format(self.document.absolute_url()),
            browser.css('#form-widgets-file a.link-overlay').first.get('href'))

        # edit should be posssible
        self.assertEqual(
            ['Keep existing file', 'Remove existing file', 'Replace with new file'],
            browser.css('#form-widgets-file label').text)

        manager.cancel()

    def test_edit_form_without_document(self):
        self.document.file = None
        self.document.digitally_available = False
        transaction.commit()

        self.browser.open('%s/edit' % self.document.absolute_url())

        self.file_field = '<input type="file" id="form-widgets-file-input" name="form.widgets.file"'

        self.assertPageContains(self.file_field)

    def test_edit_form_does_not_contain_change_note(self):
        self.browser.open('%s/edit' % self.document.absolute_url())

        # the changeNote field from IVersionable should not show up
        self.assertPageContainsNot('form.widgets.IVersionable.changeNote')

    def test_add_form_does_not_contain_change_note(self):
        self.browser.open('%s/++add++opengever.document.document' %
            self.portal.absolute_url())

        # the changeNote field from IVersionable should not show up
        self.assertPageContainsNot('form.widgets.IVersionable.changeNote')
