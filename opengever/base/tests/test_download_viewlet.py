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

    def test_without_file(self):
        test_doc = createContentInContainer(self.portal,
                                            'opengever.document.document',
                                            title=u'Doc without file',
                                            keywords=[])

        self.assertEquals('http://nohost/plone/document-1',
                          self.download(test_doc))

        self.assertResponseStatus(302) # Moved permanently

        self.assertEquals(u'No file in in this version',
                          self.ptool.showPortalMessages()[-1].message)

    def test_with_file(self):
        test_file = NamedBlobFile("lorem ipsum", filename=u"foobar.txt")
        test_doc = createContentInContainer(self.portal,
                                            'opengever.document.document',
                                            title=u'Foobar',
                                            keywords=[],
                                            file=test_file)

        self.assertEquals('lorem ipsum', self.download(test_doc))

        self.assertResponseHeader('content-disposition', 'attachment; filename="foobar.txt"')
        self.assertResponseHeader('content-length', '11', )
        self.assertResponseHeader('content-type', 'text/plain')

    def test_custom_content_type(self):
        test_file = NamedBlobFile("some text", filename=u"sometext.txt")
        test_file.contentType = 'foo/bar'
        test_doc = createContentInContainer(self.portal,
                                            'opengever.document.document',
                                            title=u'Some Text',
                                            keywords=[],
                                            file=test_file)

        self.download(test_doc)
        self.assertResponseHeader('content-type', 'foo/bar')

    def download(self, document):
        download_viewlet = document.restrictedTraverse('download_file_version')
        return download_viewlet.render()
