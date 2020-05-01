from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from opengever.bumblebee import BUMBLEBEE_VIEW_COOKIE_NAME
from opengever.tabbedview.browser.bumblebee_gallery import BumblebeeGalleryMixin
from opengever.tabbedview.browser.tabs import BaseTabProxy
from opengever.tabbedview.interfaces import ITabbedViewProxy
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.dexterity.schema import SchemaInvalidatedEvent
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface.verify import verifyClass


def set_cookie(request, value):
    # We cannot use set_preferred_listing_view from opengever.bumblebee
    # because it wont set the cookie properly in tests.
    #
    # Because that, we set the cookie value directly into the request
    request.cookies[BUMBLEBEE_VIEW_COOKIE_NAME] = value


class MockProxyTabView(BaseTabProxy):
    __name__ = 'tabbedview_view-mocktab-proxy'


class TestBaseTabProxyWithDeactivatedFeature(IntegrationTestCase):

    def test_preferred_view_name_returns_always_list_view(self):
        proxy_view = MockProxyTabView(self.portal, self.request)

        set_cookie(self.request, 'gallery')

        self.assertEqual(
            'tabbedview_view-mocktab', proxy_view.preferred_view_name)

        set_cookie(self.request, 'list')

        self.assertEqual(
            'tabbedview_view-mocktab', proxy_view.preferred_view_name)


class TestBaseTabProxyWithActivatedFeature(IntegrationTestCase):

    features = ('bumblebee',)

    def test_verify_class(self):
        verifyClass(ITabbedViewProxy, BaseTabProxy)

    def test_name_without_postfix_extract_postfix_from_view_name(self):
        proxy_view = MockProxyTabView(self.portal, self.request)

        self.assertEqual(
            'tabbedview_view-mocktab', proxy_view.name_without_postfix)

    def test_list_view_name_returns_proxy_view_name_without_postfix(self):
        proxy_view = MockProxyTabView(self.portal, self.request)

        self.assertEqual(
            'tabbedview_view-mocktab', proxy_view.list_view_name)

    def test_gallery_view_name_returns_list_view_name_with_gallery_postfix(self):
        proxy_view = MockProxyTabView(self.portal, self.request)

        self.assertEqual(
            'tabbedview_view-mocktab-gallery', proxy_view.gallery_view_name)

    def test_preferred_view_name_returns_last_used_view_name(self):
        proxy_view = MockProxyTabView(self.portal, self.request)

        set_cookie(self.request, 'gallery')

        self.assertEqual(
            'tabbedview_view-mocktab-gallery', proxy_view.preferred_view_name)

        set_cookie(self.request, 'list')

        self.assertEqual(
            'tabbedview_view-mocktab', proxy_view.preferred_view_name)


class TestBumblebeeGalleryMixin(IntegrationTestCase):

    @browsing
    def test_calling_mixin_raise_404_if_feature_is_deactivated(self, browser):
        with self.assertRaises(NotFound):
            BumblebeeGalleryMixin()(self.portal, self.request)


class TestBumblebeeGalleryMixinListViewName(IntegrationTestCase):

    def test_list_view_name_returns_view_name_for_documents_listing(self):
        self.login(self.regular_user)

        viewname = "tabbedview_view-documents-gallery"
        view = getMultiAdapter(
            (self.dossier, self.request), name=viewname)

        self.assertEqual('documents', view.list_view_name)

        viewname = "tabbedview_view-mydocuments-gallery"
        view = getMultiAdapter(
            (self.portal, self.request), name=viewname)

        self.assertEqual('mydocuments', view.list_view_name)


class TestBumblebeeGalleryMixinGetFetchUrl(IntegrationTestCase):

    features = ('bumblebee',)

    def test_get_fetch_url_returns_the_url_to_fetch_new_items(self):
        self.login(self.regular_user)

        viewname = "tabbedview_view-documents-gallery"
        view = getMultiAdapter(
            (self.dossier, self.request), name=viewname)

        self.assertEqual(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbar'
            'ungen/dossier-1/tabbedview_view-documents-gallery/fetch',
            view.get_fetch_url())

        viewname = "tabbedview_view-mydocuments-gallery"
        view = getMultiAdapter(
            (self.dossier, self.request), name=viewname)

        self.assertEqual(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbar'
            'ungen/dossier-1/tabbedview_view-mydocuments-gallery/fetch',
            view.get_fetch_url())


class TestBumblebeeGalleryMixinGetBrains(SolrIntegrationTestCase):

    def test_returns_brains_depending_on_tablesource_query(self):
        self.login(self.regular_user)

        view = getMultiAdapter(
            (self.subdossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual(['document-24', 'document-23', 'document-22'],
                         [brain.getId for brain in view.get_brains()])

    def test_brain_listing_is_cached_per_request(self):
        self.login(self.regular_user)

        view = getMultiAdapter(
            (self.subsubdossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual(1, len(view.get_brains()))

        with patch(
            'opengever.tabbedview.catalog_source.GeverCatalogTableSource.search_results'
        ) as mocked_search_results:
            view.get_brains()
        self.assertFalse(
            mocked_search_results.called, 'search_results unexpectedly called')

    @browsing
    def test_returns_only_ibumblebeeable_objects(self, browser):
        self.login(self.regular_user, browser=browser)

        # Remove IBumblebeeable behavior
        ibumblebeeable_behavior = 'ftw.bumblebee.interfaces.IBumblebeeable'
        ttool = api.portal.get_tool('portal_types')
        doc_fti = ttool.get('opengever.document.document')
        doc_fti.behaviors = [behavior for behavior in doc_fti.behaviors
                             if behavior != ibumblebeeable_behavior]
        # invalidate schema cache
        notify(SchemaInvalidatedEvent('opengever.document.document'))

        # Not an IBumblebeeable document
        create(Builder('document').within(self.subsubdossier))

        self.commit_solr()

        view = getMultiAdapter(
            (self.subsubdossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual(
            1, len(view.get_brains()),
            "Should only display one document because the second "
            "is not and IBumblebeeable object")

    @browsing
    def test_respects_searchable_text_in_request(self, browser):
        self.login(self.regular_user, browser=browser)

        view = getMultiAdapter(
            (self.dossier, self.request), name="tabbedview_view-documents-gallery")

        view.request['searchable_text'] = "Feedback"
        brains = view.get_brains()

        self.assertEqual(
            ['Feedback zum Vertragsentwurf'],
            [brain.Title for brain in brains],
        )


class TestBumblebeeGalleryMixinFetch(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    @browsing
    def test_returns_items_as_html(self, browser):
        self.login(self.regular_user, browser=browser)

        view = getMultiAdapter(
            (self.dossier, self.request), name="tabbedview_view-documents-gallery")

        browser.open_html(view.fetch())

        self.assertEqual(12, len(browser.css('.imageContainer')))

    def test_returns_empty_string_if_no_items_are_available(self):
        self.login(self.regular_user)

        view = getMultiAdapter(
            (self.empty_dossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual('', view.fetch())

    def test_returns_empty_string_if_pointer_does_not_point_to_any_object(self):
        self.login(self.regular_user)

        self.request.set('documentPointer', 20)

        view = getMultiAdapter(
            (self.dossier, self.request), name="tabbedview_view-documents-gallery")

        self.assertEqual('', view.fetch())


class TestBumblebeeGalleryViewChooserWithoutFeature(SolrIntegrationTestCase):

    @browsing
    def test_do_not_show_viewchooser_on_my_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(0, len(browser.css('.ViewChooser')))

    @browsing
    def test_do_not_show_viewchooser_on_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(0, len(browser.css('.ViewChooser')))


class TestBumblebeeGalleryViewChooser(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    @browsing
    def test_show_viewchooser_if_feature_is_activated_on_my_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(1, len(browser.css('.ViewChooser')))

    @browsing
    def test_show_viewchooser_if_feature_is_activated_on_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='tabbedview_view-mydocuments')
        self.assertEqual(1, len(browser.css('.ViewChooser')))


class TestBumblebeeGalleryView(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    @browsing
    def test_show_image_container_for_each_document(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.dossier, view="tabbedview_view-documents-gallery")

        self.assertEqual(12, len(browser.css('.imageContainer')))

    @browsing
    def test_show_fallback_message_if_no_documents_are_available(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.empty_dossier, view="tabbedview_view-documents-gallery")

        self.assertEqual(0, len(browser.css('.imageContainer')))
        self.assertEqual("No contents", browser.css('.no_content').first.text)

    @browsing
    def test_link_previews_to_bumblebee_overlay_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.dossier, view="tabbedview_view-documents-gallery")

        self.assertEqual(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbar'
            'ungen/dossier-1/task-1/document-35/@@bumblebee-overlay-listing',
            browser.css('.imageContainer').first.get('data-showroom-target'))


class TestDocumentsGalleryFetch(SolrIntegrationTestCase):

    @browsing
    def test_fetching_items_returns_html_with_items(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(
            self.dossier, view="tabbedview_view-documents-gallery/fetch")

        self.assertEqual(12, len(browser.css('.imageContainer')))


class TestMyDocumentsGalleryFetch(SolrIntegrationTestCase):

    @browsing
    def test_fetching_items_returns_html_with_items(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.portal, view="tabbedview_view-mydocuments-gallery/fetch")

        self.assertEqual(2, len(browser.css('.imageContainer')))


class TestProxyViewsWithDeactivatedFeature(SolrIntegrationTestCase):

    @browsing
    def test_do_not_set_cookie_on_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.dossier, view="tabbedview_view-documents-proxy")
        self.assertIsNone(browser.cookies.get(BUMBLEBEE_VIEW_COOKIE_NAME))

    @browsing
    def test_do_not_set_cookie_on_mydocuments_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(view="tabbedview_view-mydocuments-proxy")
        self.assertIsNone(browser.cookies.get(BUMBLEBEE_VIEW_COOKIE_NAME))

    @browsing
    def test_do_not_set_cookie_on_trash_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.dossier, view="tabbedview_view-trash-proxy")
        self.assertIsNone(browser.cookies.get(BUMBLEBEE_VIEW_COOKIE_NAME))

    @browsing
    def test_do_not_set_cookie_on_related_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.task, view="tabbedview_view-relateddocuments-proxy")
        self.assertIsNone(browser.cookies.get(BUMBLEBEE_VIEW_COOKIE_NAME))


class TestProxyViewsWithActivatedFeature(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    @browsing
    def test_documents_proxy_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.dossier, view="tabbedview_view-documents-proxy")

        self.assertEqual(
            'List',
            browser.css('.ViewChooser .active').first.text)

        # Set cookie for gallery-view
        browser.visit(self.dossier, view="tabbedview_view-documents-gallery")

        browser.visit(self.dossier, view="tabbedview_view-documents-proxy")

        self.assertEqual(
            'Gallery',
            browser.css('.ViewChooser .active').first.text)

    @browsing
    def test_dossiertemplates_documents_proxy_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.dossiertemplate, view="tabbedview_view-documents-proxy")

        self.assertEqual(
            'List',
            browser.css('.ViewChooser .active').first.text)

        # Set cookie for gallery-view
        browser.login().visit(self.dossiertemplate, view="tabbedview_view-documents-gallery")

        browser.login().visit(self.dossiertemplate, view="tabbedview_view-documents-proxy")

        self.assertEqual(
            'Gallery',
            browser.css('.ViewChooser .active').first.text)

    @browsing
    def test_mydocuments_proxy_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(
            self.portal, view="tabbedview_view-mydocuments-proxy")

        self.assertEqual(
            'List',
            browser.css('.ViewChooser .active').first.text)

        # Set cookie for gallery-view
        browser.visit(
            self.portal, view="tabbedview_view-mydocuments-gallery")

        browser.visit(view="tabbedview_view-mydocuments-proxy")

        self.assertEqual(
            'Gallery',
            browser.css('.ViewChooser .active').first.text)

    @browsing
    def test_trash_proxy_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.dossier, view="tabbedview_view-trash-proxy")

        self.assertEqual(
            'List',
            browser.css('.ViewChooser .active').first.text)

        # Set cookie for gallery-view
        browser.visit(self.dossier, view="tabbedview_view-trash-gallery")

        browser.visit(self.dossier, view="tabbedview_view-trash-proxy")

        self.assertEqual(
            'Gallery',
            browser.css('.ViewChooser .active').first.text)

    @browsing
    def test_relateddocuments_proxy_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.task, view="tabbedview_view-relateddocuments-proxy")

        self.assertEqual(
            'List',
            browser.css('.ViewChooser .active').first.text)

        # Set cookie for gallery-view
        browser.visit(self.task, view="tabbedview_view-relateddocuments-gallery")

        browser.visit(self.task, view="tabbedview_view-relateddocuments-proxy")

        self.assertEqual(
            'Gallery',
            browser.css('.ViewChooser .active').first.text)

    @browsing
    def test_select_all_use_preferred_view_content_query(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {'view_name': 'documents-proxy',
                'initialize': 0,
                'selected_count': 0}
        browser.open(self.subsubdossier, data, view='tabbed_view/select_all')

        self.assertEqual(
            ['/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossie'
             'r-1/dossier-2/dossier-4/document-23'],
            [input.get('value') for input in browser.css('input')])
