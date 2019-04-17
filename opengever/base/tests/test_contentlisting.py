from ftw.testbrowser import browsing
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.trash.trash import Trasher
from plone.app.contentlisting.interfaces import IContentListingObject


class TestOpengeverContentListing(IntegrationTestCase):
    """Test basic content listing functionality."""

    def assertCropping(self, size, value):
        self.assertEquals(
            size,
            len(value),
            'Text cropping failed for %s' % value,
            )

    def test_getIcon_returns_none_for_every_contenttype(self):
        self.login(self.regular_user)

        self.assertIsNone(
            IContentListingObject(obj2brain(self.dossier)).getIcon(),
            )

        self.assertIsNone(
            IContentListingObject(obj2brain(self.document)).getIcon(),
            )

    def test_ContentTypeClass_returns_the_contenttype_icon_css_class(self):
        self.login(self.regular_user)

        self.assertEquals(
            'contenttype-opengever-dossier-businesscasedossier',
            IContentListingObject(obj2brain(self.dossier)).ContentTypeClass(),
            )

        self.assertEquals(
            'icon-docx',
            IContentListingObject(obj2brain(self.document)).ContentTypeClass(),
            )

    def test_containing_dossier_of_a_dossier_returns_dossiers_title(self):
        self.login(self.regular_user)

        brain = obj2brain(self.dossier)
        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'.encode('utf-8'),
            IContentListingObject(brain).containing_dossier(),
            )

    def test_containing_dossier_returns_empty_string_for_object_not_in_a_dossier(self):  # noqa
        self.login(self.regular_user)

        self.assertEquals(
            '',
            IContentListingObject(
                obj2brain(self.leaf_repofolder),
                ).containing_dossier(),
            )

    def test_containing_dossier_returns_the_title_of_the_containing_dossier(self):  # noqa
        self.login(self.regular_user)

        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'.encode('utf-8'),
            IContentListingObject(
                obj2brain(self.document),
                ).containing_dossier(),
            )

    def test_containing_dossier_title_is_cropped_to_near_200_chars(self):
        self.login(self.regular_user)

        self.dossier.title = 25 * u'lorem ipsum '
        self.document.reindexObject(idxs=['containing_dossier'])

        self.assertCropping(
            201,
            IContentListingObject(
                obj2brain(self.document),
                ).containing_dossier(),
            )

    def test_cropped_title_returns_title_cropped_to_near_200_chars(self):
        self.login(self.regular_user)

        self.document.title = 25 * 'lorem ipsum '
        self.document.reindexObject()

        self.assertCropping(
            201,
            IContentListingObject(obj2brain(self.document)).CroppedTitle(),
            )

    def test_cropped_description_returns_description_cropped_to_near_400_chars(
            self,
        ):
        self.login(self.regular_user)

        self.document.description = 50 * 'lorem ipsum '
        self.document.reindexObject()

        self.assertCropping(
            399,
            IContentListingObject(
                obj2brain(self.document),
                ).CroppedDescription(),
            )

    def test_cropped_description_returns_empty_string_for_objs_without_description(self):
        self.login(self.regular_user)
        self.assertEqual('', IContentListingObject(obj2brain(self.empty_document)).CroppedDescription())

    def test_is_document(self):
        self.login(self.regular_user)

        self.assertTrue(
            IContentListingObject(obj2brain(self.document)).is_document,
            )

        self.assertFalse(
            IContentListingObject(obj2brain(self.mail_eml)).is_document,
            )

        self.assertFalse(
            IContentListingObject(obj2brain(self.dossier)).is_document,
            )

    def test_is_trashed(self):
        self.login(self.regular_user)

        self.assertFalse(
            IContentListingObject(obj2brain(self.document)).is_trashed,
            )

        Trasher(self.document).trash()

        self.assertTrue(
            IContentListingObject(
                obj2brain(self.document, unrestricted=True),
                ).is_trashed,
            )

        self.assertFalse(
            IContentListingObject(obj2brain(self.dossier)).is_trashed,
            )

    def test_is_removed(self):
        self.login(self.regular_user)

        self.assertFalse(
            IContentListingObject(obj2brain(self.dossier)).is_removed,
            )

        self.assertFalse(
            IContentListingObject(obj2brain(self.document)).is_removed,
            )

        self.login(self.manager)
        self.set_workflow_state('document-state-removed', self.document)

        self.assertTrue(
            IContentListingObject(obj2brain(self.document, unrestricted=True))
            .is_removed,
            )

    def test_get_breadcrumbs_returns_a_tuple_of_dicts_with_title_and_url(self):
        self.login(self.regular_user)

        expected_breadcrumbs = (
            {
                'Title': 'Ordnungssystem',
                'absolute_url': 'http://nohost/plone/ordnungssystem',
                },
            {
                'Title': '1. F\xc3\xbchrung',
                'absolute_url': 'http://nohost/plone/ordnungssystem/fuhrung',
                },
            {
                'Title': '1.1. Vertr\xc3\xa4ge und Vereinbarungen',
                'absolute_url': (
                    'http://nohost/plone/ordnungssystem/fuhrung'
                    '/vertrage-und-vereinbarungen'
                    ),
                },
            {
                'Title': 'Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
                'absolute_url': (
                    'http://nohost/plone/ordnungssystem/fuhrung'
                    '/vertrage-und-vereinbarungen/dossier-1'
                    ),
                },
            {
                'Title': 'Vertr\xc3\xa4gsentwurf',
                'absolute_url': (
                    'http://nohost/plone/ordnungssystem/fuhrung'
                    '/vertrage-und-vereinbarungen/dossier-1/document-14'
                    ),
                },
            )

        self.assertEquals(
            expected_breadcrumbs,
            IContentListingObject(obj2brain(self.document)).get_breadcrumbs(),
            )

    def test_responsible_fullname(self):
        self.login(self.regular_user)
        self.assertEqual(
            IContentListingObject(obj2brain(
                self.dossier)).responsible_fullname(),
            u'Ziegler Robert')


class TestBrainContentListingRenderLink(IntegrationTestCase):
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
        self.login(self.regular_user)

        self.assertEquals(
            u'PATCHED LINK Vertr\xe4gsentwurf'.encode('utf-8'),
            IContentListingObject(obj2brain(self.document)).render_link(),
            )

    def test_uses_documentlinkrenderer_for_mails(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'PATCHED LINK Die B\xfcrgschaft'.encode('utf-8'),
            IContentListingObject(obj2brain(self.mail_eml)).render_link(),
            )

    @browsing
    def test_uses_simple_renderer_for_dossiers(self, browser):
        self.login(self.regular_user)

        simple_link = (
            IContentListingObject(obj2brain(self.subdossier)).render_link()
            )

        browser.open_html(simple_link.encode('utf-8'))

        link = browser.css('a').first

        self.assertEquals('2016', link.text)
        self.assertEquals(u'2016', link.get('alt'))

        self.assertIn(
            'contenttype-opengever-dossier-businesscasedossier',
            link.get('class'),
            )


class TestOpengeverContentListingWithDisabledBumblebee(IntegrationTestCase):
    """Test we do not trip up in the lack of a bumblebee installation."""

    def setUp(self):
        super(TestOpengeverContentListingWithDisabledBumblebee, self).setUp()
        self.login(self.regular_user)
        self.obj = IContentListingObject(obj2brain(self.document))

    def test_documents_are_not_bumblebeeable(self):
        self.assertFalse(self.obj.is_bumblebeeable())

    def test_get_css_classes(self):
        self.assertEqual(
            'state-document-state-draft',
            self.obj.get_css_classes(),
            )

    def test_get_preview_image_url(self):
        self.assertIsNone(self.obj.get_preview_image_url())

    def test_get_preview_frame_url(self):
        self.assertIsNone(self.obj.get_preview_frame_url())

    def test_get_preview_pdf_url(self):
        self.assertIsNone(self.obj.get_preview_pdf_url())

    def test_get_overlay_title(self):
        self.assertIsNone(self.obj.get_overlay_title())

    def test_get_overlay_url(self):
        self.assertIsNone(self.obj.get_overlay_url())


class TestOpengeverContentListingWithEnabledBumblebee(IntegrationTestCase):
    """Test we do not trip up in the presence of a bumblebee installation."""

    features = ('bumblebee', )

    def setUp(self):
        super(TestOpengeverContentListingWithEnabledBumblebee, self).setUp()
        self.login(self.regular_user)
        self.obj = IContentListingObject(obj2brain(self.document))

    def test_documents_are_bumblebeeable(self):
        self.assertTrue(self.obj.is_bumblebeeable())

    def test_dossiers_are_not_bumblebeeable(self):
        listing = IContentListingObject(obj2brain(self.dossier))
        self.assertFalse(listing.is_bumblebeeable())

    def test_get_preview_image_url(self):
        self.assertIsNotNone(self.obj.get_preview_image_url())

    def test_get_preview_frame_url(self):
        self.assertRegexpMatches(self.obj.get_preview_frame_url(), r'/preview\?')

    def test_get_preview_pdf_url(self):
        self.assertRegexpMatches(self.obj.get_preview_pdf_url(), r'/pdf\?')

    def test_get_overlay_title(self):
        self.assertEqual(u'Vertr\xe4gsentwurf', self.obj.get_overlay_title())

    def test_get_overlay_url(self):
        expected_url = (
            '{}/@@bumblebee-overlay-listing'
            .format(self.document.absolute_url())
            )

        self.assertEqual(
            expected_url,
            self.obj.get_overlay_url())
