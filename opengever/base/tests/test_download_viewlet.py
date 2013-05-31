from Products.CMFCore.utils import getToolByName
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create
from plone.namedfile.file import NamedBlobFile


class TestDownloadViewlet(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestDownloadViewlet, self).setUp()
        self.grant('Contributor')
        self.ptool = getToolByName(self.portal, 'plone_utils')

    def test_without_file(self):
        test_doc = create(Builder("document"))

        response = self.download(test_doc)
        self.assertEquals('http://nohost/plone/document-1', response)
        self.assertResponseStatus(302) # Moved permanently
        self.assertEquals(u'No file in in this version',
                          self.ptool.showPortalMessages()[-1].message)

    def test_with_file(self):
        test_doc = create(Builder("document")
                          .attach_file_containing("lorem ipsum", name=u"foobar.txt"))

        response = self.download(test_doc)

        self.assertEquals('lorem ipsum', response)
        self.assertResponseHeader('content-disposition', 'attachment; filename="foobar.txt"')
        self.assertResponseHeader('content-length', '11', )
        self.assertResponseHeader('content-type', 'text/plain')

    def test_custom_content_type(self):
        test_file = NamedBlobFile("some text", filename=u"sometext.txt")
        test_file.contentType = 'foo/bar'
        test_doc = create(Builder("document").attach(test_file))

        self.download(test_doc)

        self.assertResponseHeader('content-type', 'foo/bar')

    def download(self, document):
        download_viewlet = document.restrictedTraverse('download_file_version')
        return download_viewlet.render()
