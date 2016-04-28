from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import deactivate_bumblebee_feature
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.tabbedview.browser.bumblebee_gallery import BumblebeeGalleryMixin
from opengever.testing import FunctionalTestCase
from plone import api
from zExceptions import NotFound
from zope.component import getMultiAdapter
import transaction


class TestBumblebeeGalleryMixin(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_calling_mixin_raise_404_if_feature_is_deactivated(self, browser):
        deactivate_bumblebee_feature()
        with self.assertRaises(NotFound):
            BumblebeeGalleryMixin()(self.portal, self.request)


class TestBumblebeeGalleryMixinListViewName(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_list_view_name_returns_view_name_for_documents_listing(self):
        dossier = create(Builder('dossier'))

        viewname = "tabbedview_view-documents-gallery"
        view = getMultiAdapter(
            (dossier, self.request), name=viewname)

        self.assertEqual('documents', view.list_view_name)

        viewname = "tabbedview_view-mydocuments-gallery"
        view = getMultiAdapter(
            (self.portal, self.request), name=viewname)

        self.assertEqual('mydocuments', view.list_view_name)


class TestBumblebeeGalleryMixinGetBrains(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_brains(self):
        dossier = create(Builder('dossier'))
        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        document = create(Builder('document').within(dossier))

        brains = view.get_brains()

        self.assertEqual([document, ], [brain.getObject() for brain in brains])

        create(Builder('document').within(dossier))
        self.assertEqual(
            1, view.number_of_documents(),
            "Should still be 1 because the catalog cache")

    def test_cache_brains(self):
        dossier = create(Builder('dossier'))
        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        create(Builder('document').within(dossier))
        self.assertEqual(1, len(view.get_brains()))

        create(Builder('document').within(dossier))
        self.assertEqual(
            1, len(view.get_brains()),
            "Should still be 1 because the catalog cache")

    @browsing
    def test_returns_only_ibumblebeeable_objects(self, browser):
        dossier = create(Builder('dossier'))

        # IBumblebeeable document
        create(Builder('document').within(dossier))

        # Remove IBumblebeeable behavior
        ibumblebeeable_behavior = 'ftw.bumblebee.interfaces.IBumblebeeable'
        ttool = api.portal.get_tool('portal_types')
        doc_fti = ttool.get('opengever.document.document')
        doc_fti.behaviors = [behavior for behavior in doc_fti.behaviors
                             if behavior != ibumblebeeable_behavior]

        transaction.commit()

        # Not an IBumblebeeable document
        create(Builder('document').within(dossier))

        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual(
            1, len(view.get_brains()),
            "Should only display one document because the second "
            "is not and IBumblebeeable object")


class TestBumblebeeGalleryMixinNumberOfDocuments(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_number_of_documents_returns_0_if_no_objects(self):
        dossier = create(Builder('dossier'))

        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual(0, view.number_of_documents())

    def test_number_of_documents_returns_the_amount_of_objects(self):
        dossier = create(Builder('dossier'))

        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        create(Builder('document').within(dossier))
        create(Builder('document').within(dossier))

        self.assertEqual(2, view.number_of_documents())


class TestBumblebeeGalleryMixinAvailable(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_available_if_more_than_0_documents(self):
        dossier = create(Builder('dossier'))
        create(Builder('document').within(dossier))

        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertTrue(view.available())

    def test_not_available_if_no_objects_to_display(self):
        dossier = create(Builder('dossier'))

        view = getMultiAdapter(
            (dossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertFalse(view.available())


class TestBumblebeeGalleryViewChooser(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_do_not_show_viewchooser_if_feature_is_deactivated_on_my_documents_tab(self, browser):
        deactivate_bumblebee_feature()
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(0, len(browser.css('.ViewChooser')))

    @browsing
    def test_show_viewchooser_if_feature_is_activated_on_my_documents_tab(self, browser):
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(1, len(browser.css('.ViewChooser')))

    @browsing
    def test_do_not_show_viewchooser_if_feature_is_deactivated_on_documents_tab(self, browser):
        deactivate_bumblebee_feature()
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(0, len(browser.css('.ViewChooser')))

    @browsing
    def test_show_viewchooser_if_feature_is_activated_on_documents_tab(self, browser):
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(1, len(browser.css('.ViewChooser')))


class TestBumblebeeGalleryView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_show_image_container_for_each_document(self, browser):
        dossier = create(Builder('dossier'))

        create(Builder('document').within(dossier))
        create(Builder('document').within(dossier))

        browser.login().visit(dossier, view="tabbedview_view-documents-gallery")

        self.assertEqual(2, len(browser.css('.imageContainer')))

    @browsing
    def test_show_fallback_message_if_no_documents_are_available(self, browser):
        dossier = create(Builder('dossier'))

        browser.login().visit(dossier, view="tabbedview_view-documents-gallery")

        self.assertEqual(0, len(browser.css('.imageContainer')))
        self.assertEqual("No contents", browser.css('.no_content').first.text)
