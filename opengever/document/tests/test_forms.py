from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles, login
from plone.namedfile.file import NamedBlobFile
from plone.testing.z2 import Browser
from zope.component import queryMultiAdapter
import transaction
import unittest2 as unittest


class TestDocumentIntegration(unittest.TestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentIntegration, self).setUp()

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))

        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(
            'opengever.document.document',
            'document-xy',
            title=u'document')

        self.document = self.portal.get('document-xy')
        self.document.keywords = ()
        self.document.file = NamedBlobFile('bla bla', filename=u'test.txt')
        self.document.digitally_available = True

        transaction.commit()

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
        self.assertFalse(
                'Keep existing file' in self.browser.contents)
        self.assertFalse(
                'Remove existing file' in self.browser.contents)
        self.assertFalse(
                'Replace with new file' in self.browser.contents)

        # save should not adjust the file
        self.browser.getControl(name="form.widgets.title").value = 'Other title'
        self.browser.getControl(name="form.buttons.save").click()

        self.assertFalse(self.document.file is None)


    def test_edit_form_document_is_checked_out(self):

        # checkout the document
        manager = queryMultiAdapter((self.document, self.document.REQUEST),
                                    ICheckinCheckoutManager)
        manager.checkout()
        transaction.commit()

        self.browser.open('%s/edit' % self.document.absolute_url())

        filename_display = '''<span class="named-file-widget namedblobfile-field" id="form-widgets-file">
    <span>
        <a class="link-overlay" href="http://nohost/plone/document-xy/file_download_confirmation">test.txt</a>
        <span class="discreet"> &mdash;
            0 KB
        </span>
    </span>'''

        self.assertTrue(filename_display in self.browser.contents)

        # edit should be posssible
        self.assertTrue(
                'Keep existing file' in self.browser.contents)
        self.assertTrue(
                'Remove existing file' in self.browser.contents)
        self.assertTrue(
                'Replace with new file' in self.browser.contents)

        manager.cancel()

    def test_edit_form_without_document(self):
        self.document.file = None
        self.document.digitally_available = False

        transaction.commit()

        self.browser.open('%s/edit' % self.document.absolute_url())

        self.file_field = '<input type="file" id="form-widgets-file-input" name="form.widgets.file" />'

        self.assertTrue(self.file_field in self.browser.contents)
