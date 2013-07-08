from ftw.builder import Builder
from ftw.builder import create
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from zope.component import queryMultiAdapter
import transaction


class TestDocumentIntegration(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestDocumentIntegration, self).setUp()
        self.grant('Manager')
        login(self.portal, TEST_USER_NAME)
        self.document = create(Builder("document")
                               .attach_file_containing(u"bla bla", name=u"test.txt")
                               .having(digitally_available=True,
                                       keywords=()))

    def test_edit_form_document_not_checked_out(self):
        self.browser.open('%s/edit' % self.document.absolute_url())

        filename_display = '''
    <span id="form-widgets-file" class="named-file-widget namedblobfile-field">
    <span>
        <span>test.txt</span>
        <span class="discreet"> &mdash; 0 KB</span>
    </span>'''

        self.assertTrue(filename_display in self.browser.contents)

        # edit should not be posssible
        self.assertPageContainsNot('Keep existing file')
        self.assertPageContainsNot('Remove existing file')
        self.assertPageContainsNot('Replace with new file')

        # save should not adjust the file
        self.browser.getControl(name="form.widgets.title").value = 'Other title'
        self.browser.getControl(name="form.buttons.save").click()
        self.assertTrue(self.document.file)


    def test_edit_form_document_is_checked_out(self):
        # checkout the document
        manager = queryMultiAdapter((self.document, self.document.REQUEST),
                                    ICheckinCheckoutManager)
        manager.checkout()
        transaction.commit()

        self.browser.open('%s/edit' % self.document.absolute_url())

        filename_display = '''<span class="named-file-widget namedblobfile-field" id="form-widgets-file">
    <span>
        <a class="link-overlay" href="http://nohost/plone/document-1/file_download_confirmation">test.txt</a>
        <span class="discreet"> &mdash;
            0 KB
        </span>
    </span>'''
        self.assertPageContains(filename_display)

        # edit should be posssible
        self.assertPageContains('Keep existing file')
        self.assertPageContains('Remove existing file')
        self.assertPageContains('Replace with new file')
        manager.cancel()

    def test_edit_form_without_document(self):
        self.document.file = None
        self.document.digitally_available = False
        transaction.commit()

        self.browser.open('%s/edit' % self.document.absolute_url())

        self.file_field = '<input type="file" id="form-widgets-file-input" name="form.widgets.file" />'

        self.assertPageContains(self.file_field)
