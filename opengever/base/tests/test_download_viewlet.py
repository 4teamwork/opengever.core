from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from opengever.testing import FunctionalTestCase

class TestDownloadViewlet(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestDownloadViewlet, self).setUp()
        self.grant('Contributor')
        self.ptool = getToolByName(self.portal, 'plone_utils')

    def test_download_viewlet(self):
        ### Download viewlet

        ## Trying to call the viewlet on a document with no file
        # Create a test document WITHOUT a file:
        test_doc0 = createContentInContainer(self.portal,
                                             'opengever.document.document',
                                             title=u'Doc without file',
                                             keywords=[])

        # Get the file download viewlet and call it:
        download_viewlet = test_doc0.restrictedTraverse('download_file_version')
        # Response should be a redirect to context:
        self.assertEquals('http://nohost/plone/document-1',
                          download_viewlet.render())

        # with status code 302 (Moved permanently):
        self.assertEquals(302, self.portal.REQUEST.response.status)

        # and a portal status message:
        self.assertEquals(u'No file in in this version',
                          self.ptool.showPortalMessages()[-1].message)
    
        ## Calling the viewlet on a document with a file
        # Create a test document with a file:
        test_file1 = NamedBlobFile("lorem ipsum", filename=u"foobar.txt")
        test_doc1 = createContentInContainer(self.portal,
                                             'opengever.document.document',
                                             title=u'Foobar',
                                             keywords=[],
                                             file=test_file1)

        # Get the file download viewlet and call it:
        download_viewlet1 = test_doc1.restrictedTraverse('download_file_version')
        # Response should contain file data:
        self.assertEquals('lorem ipsum', download_viewlet1.render())

        # Check that HTTP response headers are set correctly:
        self.assertEquals('attachment; filename="foobar.txt"',
                          self.portal.REQUEST.response.headers.get('content-disposition'))
        
        self.assertEquals('11',
                          self.portal.REQUEST.response.headers.get('content-length'))
        
        self.assertEquals('text/plain',
                          self.portal.REQUEST.response.headers.get('content-type'))
        


        ## Check that HTTP content-type header gets set correctly
        # Create a test document with a file and a custom content type:
        test_file2 = NamedBlobFile("some text", filename=u"sometext.txt")
        test_file2.contentType = 'foo/bar'
        test_doc2 = createContentInContainer(self.portal,
                                             'opengever.document.document',
                                             title=u'Some Text',
                                             keywords=[],
                                             file=test_file2)

        # Get the file download viewlet and call it:
        download_viewlet2 = test_doc2.restrictedTraverse('download_file_version')
        download_viewlet2.render()

        # Check that HTTP content-type header is set correctly:
        self.assertEquals('foo/bar', self.portal.REQUEST.response.headers.get('content-type'))
