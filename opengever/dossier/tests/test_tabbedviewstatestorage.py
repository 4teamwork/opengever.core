from ftw.builder import Builder
from ftw.builder import create
from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.tabbedview.interfaces import ITabbedViewProxy
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter


class TestDossierGridStateStorageKeyGenerator(FunctionalTestCase):

    def test_add_static_portal_type_for_dossier_types(self):
        repo, repo_folder = create(Builder('repository_tree'))
        dossier = create(Builder("dossier").within(repo_folder))

        view = dossier.restrictedTraverse('tabbedview_view-overview')

        generator = getMultiAdapter((dossier, view, self.request),
                                    IGridStateStorageKeyGenerator)

        current_type = 'opengever.dossier.businesscasedossier'
        self.assertEqual(current_type, dossier.portal_type)

        static_type = 'opengever.dossier'
        self.assertEqual(
            'ftw.tabbedview-{}-tabbedview_view-overview-test_user_1_'.format(
                static_type),
            generator.get_key())


class TestGeverTabbedviewDictStorage(FunctionalTestCase):

    def setUp(self):
        super(TestGeverTabbedviewDictStorage, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(
            Builder("dossier")
            .titled(u"Testd\xf6ssier XY")
            .within(self.repo_folder))

    def test_call_storage_with_proxy_will_change_context_to_subview(self):
        proxy_view = self.dossier.restrictedTraverse(
            'tabbedview_view-documents-proxy')

        sub_view = self.dossier.restrictedTraverse(
            'tabbedview_view-documents')

        self.assertNotIsInstance(
            IDictStorage(sub_view).context, proxy_view.__class__)
        self.assertIsInstance(
            IDictStorage(sub_view).context, sub_view.__class__)

    def test_call_storage_with_subview_will_not_change_context(self):
        sub_view = self.dossier.restrictedTraverse(
            'tabbedview_view-documents')

        self.assertIsInstance(
            IDictStorage(sub_view).context, sub_view.__class__)

    def test_strip_proxy_returns_proxy_view_without_postfix(self):
        view = self.dossier.restrictedTraverse('tabbedview_view-documents-proxy')

        self.assertTrue(ITabbedViewProxy.providedBy(view))
        self.assertEqual(
            'tabbedview_view-documents',
            IDictStorage(view).strip_proxy_postfix(view, view.__name__))

    def test_strip_proxy_postfix_will_replace_only_if_ITabbedViewProxy_is_provided(self):
        view = self.dossier.restrictedTraverse('tabbedview_view-documents')
        value = 'documents_view-documents-proxy'

        self.assertFalse(ITabbedViewProxy.providedBy(view))
        self.assertEqual(
            'documents_view-documents-proxy',
            IDictStorage(view).strip_proxy_postfix(view, value))
