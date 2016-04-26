from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from zExceptions import NotFound
from opengever.core.testing import deactivateBumblebeeFeature


class TestBumblebeeGalleryViewFeature(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_raise_404_on_galleryview_if_feature_is_deactivated(self, browser):
        deactivateBumblebeeFeature()
        with self.assertRaises(NotFound):
            browser.login().open(self.portal, view='tabbedview_view-galleryview')

    @browsing
    def test_render_galleryview_if_feature_is_activated(self, browser):
        browser.login().open(self.portal, view='tabbedview_view-galleryview')
        self.assertEqual(1, len(browser.css('.preview-listing')))

    @browsing
    def test_do_not_show_viewchooser_if_feature_is_deactivated_on_my_documents_tab(self, browser):
        deactivateBumblebeeFeature()
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(0, len(browser.css('.ViewChooser')))

    @browsing
    def test_show_viewchooser_if_feature_is_activated_on_my_documents_tab(self, browser):
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(1, len(browser.css('.ViewChooser')))

    @browsing
    def test_do_not_show_viewchooser_if_feature_is_deactivated_on_documents_tab(self, browser):
        deactivateBumblebeeFeature()
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(0, len(browser.css('.ViewChooser')))

    @browsing
    def test_show_viewchooser_if_feature_is_activated_on_documents_tab(self, browser):
        browser.login().open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(1, len(browser.css('.ViewChooser')))


class TestBumblebeeGalleryView(FunctionalTestCase):

    def setUp(self):
        super(TestBumblebeeGalleryView, self).setUp()

        self.dossier = create(Builder('dossier'))

    @browsing
    def test_display_only_ibumblebeeable_objects(self, browser):

        # providing IBumblebeeable
        create(Builder('document').within(self.dossier))

        # not providing IBumblebeeable
        create(Builder('task').within(self.dossier))

        browser.login().visit(self.dossier, view='tabbedview_view-galleryview')
        self.assertEqual(1, len(browser.css('.previewitem')))

    @browsing
    def test_filtering_works(self, browser):
        page = browser.login().visit(self.workspace, view='tabbedview_view-documents', data={'searchable_text':"bla"})
        self.assertEqual(1, len(page.css('.previewitem')))
        self.assertEqual("ein blatt Papier", page.css('.previewitem').first.text)


# class TestPreview(FunctionalTestCase):

#     def setUp(self):
#         self.portal = self.layer['portal']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
#         login(self.portal, TEST_USER_NAME)

#         self.workspace = create(Builder('workspace'))

#         self.portal.portal_types.get(
#             'Workspace').allowed_content_types = ('File', 'Image')

#         self.bumble1 = create(Builder('file').titled("ein blatt Papier").within(self.workspace))
#         self.bumble2 = create(Builder('file').within(self.workspace))
#         self.bumble3 = create(Builder('file').within(self.workspace))
#         self.nobumble = create(Builder('image').within(self.workspace))

#     @browsing
#     def test_only_bumblebeeable_displayed(self, browser):
#         page = browser.login().visit(self.workspace, view='tabbedview_view-documents')
#         self.assertEqual(3, len(page.css('.previewitem')))

#     @browsing
#     def test_filtering_works(self, browser):
#         page = browser.login().visit(self.workspace, view='tabbedview_view-documents', data={'searchable_text':"bla"})
#         self.assertEqual(1, len(page.css('.previewitem')))
#         self.assertEqual("ein blatt Papier", page.css('.previewitem').first.text)


# class TestLazy(FunctionalTestCase):

#     def setUp(self):
#         self.portal = self.layer['portal']
#         self.request = self.layer['request']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
#         login(self.portal, TEST_USER_NAME)

#         self.workspace = create(Builder('workspace'))

#         self.portal.portal_types.get(
#             'Workspace').allowed_content_types = ('File', 'Image')

#     def test_available_if_there_are_documents(self):
#         view = DocumentsTab(self.workspace, self.request)

#         create(Builder('file').within(self.workspace))

#         self.assertTrue(view.available())

#     def test_not_available_if_there_are_no_documents(self):
#         view = DocumentsTab(self.workspace, self.request)
#         self.assertFalse(view.available())

#     def test_number_of_documents(self):
#         view = DocumentsTab(self.workspace, self.request)
#         create(Builder('file').within(self.workspace))
#         create(Builder('file').within(self.workspace))

#         self.assertEqual(view.number_of_documents(), 2)

#     def test_returns_from_the_given_next_document_id(self):
#         view = DocumentsTab(self.workspace, self.request)
#         create(Builder('file').within(self.workspace).titled('doc_0'))
#         create(Builder('file').within(self.workspace).titled('doc_1'))
#         create(Builder('file').within(self.workspace).titled('doc_2'))
#         create(Builder('file').within(self.workspace).titled('doc_3'))

#         view.amount_preloaded_documents = 2

#         self.assertEqual(
#             [0, 1],
#             [item.get('document_id') for item in view.previews()],
#             "There should be only two items, starting at 0")

#     def test_returns_from_next_document_id_the_given_amount(self):
#         view = DocumentsTab(self.workspace, self.request)
#         create(Builder('file').within(self.workspace).titled('doc_0'))
#         create(Builder('file').within(self.workspace).titled('doc_1'))
#         create(Builder('file').within(self.workspace).titled('doc_2'))
#         create(Builder('file').within(self.workspace).titled('doc_3'))

#         view.amount_preloaded_documents = 2
#         self.request.set('next_document_id', 2)

#         self.assertEqual(
#             [2, 3],
#             [item.get('document_id') for item in view.previews()],
#             "There should be only two items starting at 2")

#     @browsing
#     def test_fetch_url_returns_items_as_html(self, browser):
#         create(Builder('file').within(self.workspace).titled('doc_0'))
#         create(Builder('file').within(self.workspace).titled('doc_1'))

#         browser.login().visit(
#             self.workspace,
#             view="tabbedview_view-documentpreview/fetch")

#         self.assertEqual(
#             2, len(browser.css('.imageContainer')))
