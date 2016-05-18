from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.utils import get_representation_url_by_brain
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.contentlisting.interfaces import IContentListingObject


class TestOpengeverContentListing(FunctionalTestCase):

    def test_getIcon_returns_none_for_every_contenttype(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document'))

        self.assertEquals(
            None,
            IContentListingObject(obj2brain(dossier)).getIcon())

        self.assertEquals(
            None,
            IContentListingObject(obj2brain(document)).getIcon())

    def test_ContentTypeClass_returns_the_contenttype_icon_css_class(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document'))

        self.assertEquals(
            'contenttype-opengever-dossier-businesscasedossier',
            IContentListingObject(obj2brain(dossier)).ContentTypeClass())

        self.assertEquals(
            'contenttype-opengever-document-document',
            IContentListingObject(obj2brain(document)).ContentTypeClass())

    def test_containing_dossier_of_a_dossier_returns_dossiers_title(self):
        dossier = create(Builder('dossier').titled(u'Testdossier'))

        self.assertEquals(
            'Testdossier',
            IContentListingObject(obj2brain(dossier)).containing_dossier())

    def test_containing_dossier_returns_empty_string_for_object_not_in_a_dossier(self):
        repository = create(Builder('repository'))

        self.assertEquals(
            '',
            IContentListingObject(obj2brain(repository)).containing_dossier())

    def test_containing_dossier_returns_the_title_of_the_containing_dossier(self):
        dossier = create(Builder('dossier').titled(u'Testdossier'))
        document = create(Builder('document').within(dossier))

        self.assertEquals(
            'Testdossier',
            IContentListingObject(obj2brain(document)).containing_dossier())

    def test_containing_dossier_title_is_cropped_to_near_200_chars(self):
        dossier = create(Builder('dossier')
                         .titled(25 * u'lorem ipsum '))
        document = create(Builder('document').within(dossier))

        self.assertCropping(
            201, IContentListingObject(obj2brain(document)).containing_dossier())

    def test_cropped_title_returns_title_cropped_to_near_200_chars(self):
        document = create(Builder('document')
                          .titled(25 * 'lorem ipsum '))

        self.assertCropping(
            201, IContentListingObject(obj2brain(document)).CroppedTitle())

    def test_cropped_description_returns_description_cropped_to_near_400_chars(self):
        document = create(Builder('document')
                          .having(description=50 * 'lorem ipsum '))

        self.assertCropping(
            399, IContentListingObject(obj2brain(document)).CroppedDescription())

    def test_cropped_description_returns_empty_string_for_objs_without_description(self):
        document = create(Builder('document'))

        self.assertEquals(
            '', IContentListingObject(obj2brain(document)).CroppedDescription())

    def assertCropping(self, size, value):
        self.assertEquals(
            size, len(value), 'Text cropping failed for %s' % value)


class TestOpengeverContentListingWithDisabledBumblebee(FunctionalTestCase):

    def setUp(self):
        super(TestOpengeverContentListingWithDisabledBumblebee, self).setUp()

        document = create(Builder('document'))
        self.obj = IContentListingObject(obj2brain(document))

    def test_documents_are_not_bumblebeeable(self):
        self.assertFalse(self.obj.is_bumblebeeable())

    def test_get_css_classes(self):
        self.assertEqual('state-document-state-draft',
                         self.obj.get_css_classes())

    def test_get_preview_image_url(self):
        self.assertIsNone(self.obj.get_preview_image_url())

    def test_get_overlay_title(self):
        self.assertIsNone(self.obj.get_overlay_title())

    def test_get_overlay_url(self):
        self.assertIsNone(self.obj.get_overlay_url())


class TestOpengeverContentListingWithEnabledBumblebee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestOpengeverContentListingWithEnabledBumblebee, self).setUp()

        document = create(Builder('document')
                          .with_dummy_content())
        self.obj = IContentListingObject(obj2brain(document))

    def test_documents_are_bumblebeeable(self):
        self.assertTrue(self.obj.is_bumblebeeable())

    def test_dossiers_are_not_bumblebeeable(self):
        dossier = create(Builder('dossier'))
        listing = IContentListingObject(obj2brain(dossier))

        self.assertFalse(listing.is_bumblebeeable())

    def test_get_css_classes_extended_with_showroom_item_class(self):
        self.assertEqual('state-document-state-draft showroom-item',
                         self.obj.get_css_classes())

    def test_get_preview_image_url(self):
        self.assertIsNotNone(self.obj.get_preview_image_url())

    def test_get_overlay_title(self):
        self.assertEqual(u'Testdokum\xe4nt'.encode('utf-8'),
                         self.obj.get_overlay_title())

    def test_get_overlay_url(self):
        self.assertEqual('http://nohost/plone/document-1/@@bumblebee-overlay-listing',
                         self.obj.get_overlay_url())
