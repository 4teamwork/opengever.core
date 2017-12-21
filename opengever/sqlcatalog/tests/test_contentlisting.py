from opengever.sqlcatalog.interfaces import ISQLCatalog
from opengever.testing import IntegrationTestCase
from plone.app.contentlisting.interfaces import IContentListingObject
from zope.component import getUtility


class TestContentListing(IntegrationTestCase):

    def setUp(self):
        super(TestContentListing, self).setUp()
        self.login(self.regular_user)
        self.record = getUtility(ISQLCatalog).get_record_for(self.document)
        self.item = IContentListingObject(self.record)

    def test_getId(self):
        self.assertEquals('document-4', self.item.getId())

    def test_getObject(self):
        self.assertEquals(self.document, self.item.getObject())

    def test_getDataOrigin(self):
        self.assertEquals(self.record, self.item.getDataOrigin())

    def test_getPath(self):
        self.assertEquals(
            u'/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-4',
            self.item.getPath())

    def test_getURL(self):
        self.assertEquals(
            u'http://nohost/plone/ordnungssystem/fuhrung/'
            u'vertrage-und-vereinbarungen/dossier-1/document-4',
            self.item.getURL())

    def test_uuid(self):
        self.assertEquals(u'createtreatydossiers000000000002', self.item.uuid())

    def test_getIcon(self):
        self.assertEquals(u'docx.png', self.item.getIcon())

    def test_getSize(self):
        # We don't need that now.
        self.assertIsNone(self.item.getSize())

    def test_review_state(self):
        self.assertEquals(u'document-state-draft', self.item.review_state())

    def test_PortalType(self):
        self.assertEquals(u'opengever.document.document', self.item.PortalType())

    def test_CroppedDescription(self):
        # We don't need that now.
        self.assertIsNone(self.item.CroppedDescription())

    def test_ContentTypeClass(self):
        self.assertEquals('contenttype-opengever-document-document', self.item.ContentTypeClass())
