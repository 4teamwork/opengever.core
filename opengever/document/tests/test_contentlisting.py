from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.contentlisting.interfaces import IContentListingObject


class TestDocumentContentListingObject(FunctionalTestCase):

    def test_contenttypeclass_is_normalized_mimetype(self):
        document = create(Builder('document')
                          .attach_file_containing('DATA', u'test.pdf'))

        self.assertEquals(
            'icon-pdf',
            IContentListingObject(document).ContentTypeClass())

    def test_is_a_document(self):
        document = create(Builder('document'))
        self.assertTrue(IContentListingObject(document).is_document)

    def test_is_trashed(self):
        self.grant('Administrator')

        document_a = create(Builder('document'))
        document_b = create(Builder('document').trashed())

        self.assertFalse(IContentListingObject(document_a).is_trashed)
        self.assertTrue(IContentListingObject(document_b).is_trashed)

    def test_is_removed(self):
        self.grant('Administrator')

        document_a = create(Builder('document'))
        document_b = create(Builder('document').trashed())
        document_c = create(Builder('document').removed())

        self.assertFalse(IContentListingObject(document_a).is_removed)
        self.assertFalse(IContentListingObject(document_b).is_removed)
        self.assertTrue(IContentListingObject(document_c).is_removed)

    def test_is_not_bumblebeeable_when_feature_is_disabled(self):
        document = create(Builder('document'))
        self.assertFalse(IContentListingObject(document).is_bumblebeeable())

    def test_preview_image_url_is_none_when_bumblebee_is_disabled(self):
        document = create(Builder('document'))
        self.assertIsNone(
            IContentListingObject(document).preview_image_url())

    def test_overlay_url_is_none_when_bumblebee_is_disabled(self):
        document = create(Builder('document'))
        self.assertIsNone(
            IContentListingObject(document).get_overlay_url())

    def test_overlay_title_is_document_title_utf8_encoded(self):
        document = create(Builder('document')
                          .titled('Anfrage B\xc3\xbcchel'.decode('utf-8')))

        self.assertEquals(
            u'Anfrage B\xfcchel',
            IContentListingObject(document).get_overlay_title())

    def test_get_breadcrumbs_returns_a_tuple_of_dicts_with_title_and_url(self):
        root = create(Builder('repository_root').titled(u'Ordnungssystem'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Ablage 1'))
        dossier = create(Builder('dossier')
                         .within(repo)
                         .titled('hans m\xc3\xbcller'.decode('utf-8')))
        document = create(Builder('document')
                          .titled('Anfrage Meier')
                          .within(dossier)
                          .with_dummy_content())

        self.assertEquals(
            ({'absolute_url': 'http://nohost/plone/ordnungssystem',
              'Title': 'Ordnungssystem'},
             {'absolute_url': 'http://nohost/plone/ordnungssystem/ablage-1',
              'Title': '1. Ablage 1'},
             {'absolute_url': 'http://nohost/plone/ordnungssystem/ablage-1/dossier-1',
              'Title': 'hans m\xc3\xbcller'},
             {'absolute_url': 'http://nohost/plone/ordnungssystem/ablage-1/dossier-1/document-1',
              'Title': 'Anfrage Meier'}),
            IContentListingObject(document).get_breadcrumbs())


class TestDocumentContentListingObjectWithBumblebee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_is_bumblebeeable_when_feature_is_enabled(self):
        document = create(Builder('document'))
        self.assertTrue(IContentListingObject(document).is_bumblebeeable())

    def test_preview_image_url_is_representation_url(self):
        document = create(Builder('document').with_dummy_content())
        url = IContentListingObject(document).preview_image_url()
        self.assertTrue(
            url.startswith('http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/'))

    def test_overlay_url_is_bumblebee_overlay_listing_view(self):
        document = create(Builder('document').with_dummy_content())
        self.assertEquals(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            IContentListingObject(document).get_overlay_url())
