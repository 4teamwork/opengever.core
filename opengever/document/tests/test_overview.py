from ftw.testing import MockTestCase
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD, login
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobFile
from plone.testing.z2 import Browser
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
import transaction


class TestDocumentOverview(MockTestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

    def _set_default_values(self, doc):
        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        doc.description = u'Lorem ipsumldkfj\r\nsdflsdfio'
        doc.file = monk_file
        doc.keywords = ()
        doc.digitally_available = True
        doc.preserved_as_paper = True

    def setUp(self):
        super(TestDocumentOverview, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))

        # document 1
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(
            'opengever.document.document', 'document-xy', title=u'document')
        self.document = self.portal.get('document-xy')

        self._set_default_values(self.document)

        # document2 (checked out by TEST_USER_ID)
        self.portal.invokeFactory(
            'opengever.document.document', 'document-2', title=u'document2')
        self.document2 = self.portal.get('document-2')
        self._set_default_values(self.document2)

        manager = queryMultiAdapter(
            (self.document2, self.portal.REQUEST), ICheckinCheckoutManager)
        manager.checkout()

        # document3 (checked out by hugo.boss)
        self.portal.invokeFactory(
            'opengever.document.document', 'document-3', title=u'document3')
        self.document3 = self.portal.get('document-3')
        self._set_default_values(self.document3)
        IAnnotations(self.document3)[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = 'hugo.boss'

        transaction.commit()

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        super(TestDocumentOverview, self).tearDown()

    def test_overview(self):

        self.browser.open(
            '%s/tabbedview_view-overview' % self.document.absolute_url())

        # edit link is available
        edit_link = """<a class="function-edit" href="http://nohost/plone/document-xy/editing_document">
            Edit Document
          </a>"""
        self.assertTrue(edit_link in self.browser.contents)

        # creator link
        creator_link = """<th>creator</th>
			<td><a href="http://nohost/plone/@@user-details/test_user_1_">Boss Hugo (test_user_1_)</a></td>"""
        self.assertTrue(creator_link in self.browser.contents)

        # copy link
        copy_link = '<a class="function-download-copy link-overlay" href="http://nohost/plone/document-xy/file_download_confirmation">Download copy</a>'
        self.assertTrue(copy_link in self.browser.contents)

    def test_overview_self_checked_out(self):
        """Check the document overview when the document is checked out,
        by your self (TEST_USER_ID):
         - checked out by information
         - edit link is still available"""

        self.browser.open(
            '%s/tabbedview_view-overview' % self.document2.absolute_url())

        checked_out_info = """<th>Checked out</th>
			<td><a href="http://nohost/plone/@@user-details/test_user_1_">Boss Hugo (test_user_1_)</a></td>"""
        self.assertTrue(checked_out_info in self.browser.contents)

        edit_link = """<a class="function-edit" href="http://nohost/plone/document-2/editing_document">
            Edit Document
          </a>"""
        self.assertTrue(edit_link in self.browser.contents)

        active_copy_download_link = """<a class="function-download-copy link-overlay" href="http://nohost/plone/document-2/file_download_confirmation">Download copy</a>"""
        self.assertTrue(active_copy_download_link in self.browser.contents)

    def test_over_other_checked_out(self):
        """Check the document overview when the document is checked out,
        by another user:
         - checked out information
         - edit link is inactive"""

        self.browser.open(
            '%s/tabbedview_view-overview' % self.document3.absolute_url())

        inactive_edit_link = """<span class="function-edit-inactive discreet">
            Edit Document
          </span>"""
        self.assertTrue(inactive_edit_link in self.browser.contents)

        inactive_copy_download_link = """<span class="function-download-copy-inactive link-overlay discreet">Download copy</span>"""
        self.assertTrue(inactive_copy_download_link in self.browser.contents)
