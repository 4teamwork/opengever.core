from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.contentlisting.interfaces import IContentListingObject


class TestOpengeverContentListing(FunctionalTestCase):
    """Test basic content listing functionality."""

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

    def test_containing_dossier_returns_empty_string_for_object_not_in_a_dossier(self):  # noqa
        repository = create(Builder('repository'))

        self.assertEquals(
            '',
            IContentListingObject(obj2brain(repository)).containing_dossier())

    def test_containing_dossier_returns_the_title_of_the_containing_dossier(self):  # noqa
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
            201,
            IContentListingObject(obj2brain(document)).containing_dossier(),
            )

    def test_cropped_title_returns_title_cropped_to_near_200_chars(self):
        document = create(Builder('document')
                          .titled(25 * 'lorem ipsum '))

        self.assertCropping(
            201, IContentListingObject(obj2brain(document)).CroppedTitle())

    def test_cropped_description_returns_description_cropped_to_near_400_chars(self):  # noqa
        document = create(Builder('document')
                          .having(description=50 * 'lorem ipsum '))

        self.assertCropping(
            399,
            IContentListingObject(obj2brain(document)).CroppedDescription(),
            )

    def test_cropped_description_returns_empty_string_for_objs_without_description(self):  # noqa
        document = create(Builder('document'))

        self.assertEquals(
            '',
            IContentListingObject(obj2brain(document)).CroppedDescription(),
            )

    def assertCropping(self, size, value):
        self.assertEquals(
            size, len(value), 'Text cropping failed for %s' % value)

    def test_is_document(self):
        document = create(Builder('document'))
        mail = create(Builder('mail'))
        dossier = create(Builder('dossier'))

        self.assertTrue(IContentListingObject(obj2brain(document)).is_document)
        self.assertFalse(IContentListingObject(obj2brain(mail)).is_document)
        self.assertFalse(IContentListingObject(obj2brain(dossier)).is_document)

    def test_is_trashed(self):
        self.grant('Administrator')
        document_a = create(Builder('document'))
        document_b = create(Builder('document').trashed())

        dossier = create(Builder('dossier'))

        self.assertFalse(
            IContentListingObject(obj2brain(document_a)).is_trashed)
        self.assertTrue(
            IContentListingObject(obj2brain(document_b, unrestricted=True))
            .is_trashed)
        self.assertFalse(IContentListingObject(obj2brain(dossier)).is_trashed)

    def test_is_removed(self):
        document_a = create(Builder('document'))
        document_b = create(Builder('document').removed())
        dossier = create(Builder('dossier'))

        self.assertFalse(
            IContentListingObject(obj2brain(document_a)).is_removed)
        self.assertTrue(
            IContentListingObject(obj2brain(document_b, unrestricted=True))
            .is_removed)
        self.assertFalse(IContentListingObject(obj2brain(dossier)).is_removed)

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
             {'absolute_url': 'http://nohost/plone/ordnungssystem/ablage-1/dossier-1',  # noqa
              'Title': 'hans m\xc3\xbcller'},
             {'absolute_url': 'http://nohost/plone/ordnungssystem/ablage-1/dossier-1/document-1',  # noqa
              'Title': 'Anfrage Meier'}),
            IContentListingObject(obj2brain(document)).get_breadcrumbs())


class TestBrainContentListingRenderLink(FunctionalTestCase):
    """Test we render appropriate content listing links per content type."""

    def setUp(self):
        super(TestBrainContentListingRenderLink, self).setUp()

        # Because the DocumentLinkWidget is already tested in a separate
        # testcase, we replace them with a simple patch for this test.
        def patched_link_render(self):
            return 'PATCHED LINK {}'.format(self.document.Title())

        self.org_render = DocumentLinkWidget.render
        DocumentLinkWidget.render = patched_link_render

    def tearDown(self):
        DocumentLinkWidget.render = self.org_render
        super(TestBrainContentListingRenderLink, self).tearDown()

    def test_uses_documentlinkrenderer_for_documents(self):
        document = create(Builder('document').titled(u'Document A'))

        self.assertEquals(
            'PATCHED LINK Document A',
            IContentListingObject(obj2brain(document)).render_link())

    def test_uses_documentlinkrenderer_for_mails(self):
        mail = create(Builder('mail').titled(u'Mail A'))

        self.assertEquals(
            'PATCHED LINK Mail A',
            IContentListingObject(obj2brain(mail)).render_link())

    def test_uses_simple_renderer_for_dossiers(self):
        dossier = create(Builder('dossier').titled(u'D\xf6ssier A'))

        simple_link = IContentListingObject(obj2brain(dossier)).render_link()
        self.assertIn(u'href="http://nohost/plone/dossier-1"', simple_link)
        self.assertIn(u'alt="D\xf6ssier A"', simple_link)
        self.assertIn(
            u'class="contenttype-opengever-dossier-businesscasedossier"',
            simple_link,
            )
        self.assertIn(u'>D\xf6ssier A</a>\n', simple_link)


class TestOpengeverContentListingWithDisabledBumblebee(FunctionalTestCase):
    """Test we do not trip up in the lack of a bumblebee installation."""

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
    """Test we do not trip up in the presence of a bumblebee installation."""

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

    def test_get_preview_image_url(self):
        self.assertIsNotNone(self.obj.get_preview_image_url())

    def test_get_overlay_title(self):
        self.assertEqual(u'Testdokum\xe4nt', self.obj.get_overlay_title())

    def test_get_overlay_url(self):
        self.assertEqual(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            self.obj.get_overlay_url(),
            )
