from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from ftw.testbrowser import browsing
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.document.interfaces import IFileCopyDownloadedEvent
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
import transaction


class TestDocumentDownloadView(MockTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentDownloadView, self).setUp()
        self.portal = self.layer['portal']

        create(Builder('fixture').with_admin_unit())

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        session.current_session = session.factory()
        session.current_session.portal = self.portal

    def tearDown(self):
        super(TestDocumentDownloadView, self).tearDown()
        session.current_session = None

    def test_download_view(self):
        doc1 = create(Builder("document").attach_file_containing("bla bla"))
        doc2 = create(Builder("document")
                      .attach_file_containing("blub blub", name=u't\xf6st.txt'))

        downloaded_handler = self.mocker.mock()
        self.mock_handler(downloaded_handler, [IFileCopyDownloadedEvent, ])
        self.expect(downloaded_handler(ANY)).count(2).result(True)

        self.replay()

        result = doc1.unrestrictedTraverse('download')()
        result.seek(0)
        self.assertEquals(result.read(), 'bla bla')

        result = doc2.unrestrictedTraverse('download')()
        result.seek(0)
        self.assertEquals(result.read(), 'blub blub')

    def test_download_file_version_view(self):
        doc1 = create(Builder("document"))

        repo_tool = getToolByName(self.portal, 'portal_repository')
        repo_tool._recursiveSave(doc1, {},
                                 repo_tool._prepareSysMetadata('mock'),
                                 autoapply=repo_tool.autoapply)

        monk_file = NamedBlobFile('bla bla', filename=u'test.txt')
        doc1.file = monk_file

        # create version
        repo_tool = getToolByName(self.portal, 'portal_repository')
        repo_tool._recursiveSave(doc1, {},
                                 repo_tool._prepareSysMetadata('mock'),
                                 autoapply=repo_tool.autoapply)

        downloaded_handler = self.mocker.mock()
        self.mock_handler(downloaded_handler, [IFileCopyDownloadedEvent, ])
        self.expect(downloaded_handler(ANY)).result(True)

        self.replay()

        # second version with a document
        doc1.REQUEST['version_id'] = '2'
        result = doc1.unrestrictedTraverse('download_file_version')()
        self.assertEquals(result, 'bla bla')

        # first version with a document
        self.portal.REQUEST['version_id'] = '1'
        result = doc1.unrestrictedTraverse('download_file_version')()
        # result should be a redirect back to the document
        self.assertEquals(result, 'http://nohost/plone/document-1')


class TestDocumentDownloadConfirmation(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestDocumentDownloadConfirmation, self).setUp()
        self.grant('Manager')
        login(self.portal, TEST_USER_NAME)
        self.document = create(Builder("document"))

        file_ = NamedBlobFile('bla bla', filename=u'test.txt')
        self.document.file = file_

        # create version
        repo_tool = getToolByName(self.portal, 'portal_repository')
        repo_tool._recursiveSave(self.document, {},
                                 repo_tool._prepareSysMetadata('mock'),
                                 autoapply=repo_tool.autoapply)
        transaction.commit()

    @browsing
    def test_download_confirmation_for_empty_file(self, browser):
        self.document.file = None
        transaction.commit()

        browser.login().open(self.document, view='file_download_confirmation')
        self.assertIn(
            u'The Document {0} has no File'.format(self.document.Title()),
            browser.contents)

    def test_download_confirmation_view_for_download(self):
        self.browser.open(
            '%s/file_download_confirmation' % self.document.absolute_url())

        self.assertIn("You\'re downloading a copy of the document",
                      self.browser.locate(".details > p").text)

        # submit
        self.browser.getControl('label_download').click()
        self.assertEquals(
            self.browser.url, '%s/download' % (self.document.absolute_url()))

    def test_download_confirmation_view_for_version_download(self):
        self.browser.open(
            '%s/file_download_confirmation?version_id=1' % (
                self.document.absolute_url()))

        self.assertIn("You're downloading a copy of the document",
                      self.browser.locate(".details > p").text)

        # submit
        self.browser.getControl('label_download').click()

        self.assertEquals(
            self.browser.url,
            '%s/download_file_version?version_id=1' % (
                self.document.absolute_url()))
