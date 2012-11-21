from Products.CMFCore.utils import getToolByName
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.document.interfaces import IFileCopyDownloadedEvent
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD, login
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.testing.z2 import Browser
import transaction
import unittest2 as unittest


class TestDocumentDownloadView(MockTestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

    def test_download_view(self):
        portal = self.layer['portal']

        doc1 = createContentInContainer(
            portal, 'opengever.document.document', 'document')

        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        doc1.file = monk_file

        downloaded_handler = self.stub()
        self.mock_handler(downloaded_handler, [IFileCopyDownloadedEvent, ])
        self.expect(downloaded_handler(ANY)).result(True)

        self.replay()
        result = doc1.unrestrictedTraverse('download')()


class TestDocumentDownloadConfirmation(unittest.TestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentDownloadConfirmation, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))

        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(
            'opengever.document.document', 'document-xy', title='document')

        self.document = self.portal.get('document-xy')
        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        self.document.file = monk_file

        # create version
        repo_tool = getToolByName(self.portal, 'portal_repository')
        repo_tool._recursiveSave(self.document, {},
                                 repo_tool._prepareSysMetadata('mock'),
                                 autoapply=repo_tool.autoapply)

        transaction.commit()

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        super(TestDocumentDownloadConfirmation, self).tearDown()

    def test_download_confirmation_view_for_download(self):
        self.browser.open(
            '%s/file_download_confirmation' % self.document.absolute_url())

        error_msg = """<p>You\'re downloading a copy of the document
          <span>test.txt</span>
        </p>"""

        self.assertTrue(error_msg in self.browser.contents)

        # submit
        self.browser.getControl('label_download').click()
        self.assertEquals(
            self.browser.url, '%s/download' % (self.document.absolute_url()))

    def test_download_confirmation_view_for_version_download(self):
        self.browser.open(
            '%s/file_download_confirmation?version_id=1' % (
                self.document.absolute_url()))

        error_msg = """<p>You\'re downloading a copy of the document
          <span>test.txt</span>
        </p>"""

        self.assertTrue(error_msg in self.browser.contents)

        # submit
        self.browser.getControl('label_download').click()

        self.assertEquals(
            self.browser.url,
            '%s/download_file_version?version_id=1' % (
                self.document.absolute_url()))
