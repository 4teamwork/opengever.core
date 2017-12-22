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

    def test_Title(self):
        self.assertEquals('Vertr\xc3\xa4gsentwurf', self.item.Title())

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

    def test_is_document(self):
        self.assertTrue(self.item.is_document)

    def test_is_trashed(self):
        self.assertFalse(self.item.is_trashed)

    def test_is_removed(self):
        self.assertFalse(self.item.is_removed)

    def test_is_bumblebeeable(self):
        self.assertFalse(self.item.is_bumblebeeable())
        self.activate_feature('bumblebee')
        self.assertTrue(self.item.is_bumblebeeable())

    def test_is_render_link(self):
        self.assertTrue(self.item.render_link())

    def test_get_breadcrumbs(self):
        self.assertEquals(
            ({'Title': 'Ordnungssystem',
              'absolute_url': 'http://nohost/plone/ordnungssystem'},
             {'Title': '1. F\xc3\xbchrung',
              'absolute_url': 'http://nohost/plone/ordnungssystem/fuhrung'},
             {'Title': '1.1. Vertr\xc3\xa4ge und Vereinbarungen',
              'absolute_url': 'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'},
             {'Title': 'Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
              'absolute_url': 'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'},
             {'Title': 'Vertr\xc3\xa4gsentwurf',
              'absolute_url': 'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-4'}),
            self.item.get_breadcrumbs())

    def test_get_overlay_url(self):
        self.activate_feature('bumblebee')
        self.assertEquals(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
            '/dossier-1/document-4/@@bumblebee-overlay-listing',
            self.item.get_overlay_url())

    def test_get_preview_image_url(self):
        self.activate_feature('bumblebee')
        self.assertEquals(
            'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local'
            '/51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2'
            '/thumbnail',
            self.item.get_preview_image_url().split('?')[0])

    def test_get_overlay_title(self):
        self.assertEquals(u'Vertr\xe4gsentwurf', self.item.get_overlay_title())
