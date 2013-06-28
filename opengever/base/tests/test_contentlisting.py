from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create
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
