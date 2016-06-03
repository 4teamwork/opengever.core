from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from ftw.dictstorage.interfaces import IDictStorage


class TestGeverTabbedviewDictStorage(FunctionalTestCase):

    def setUp(self):
        super(TestGeverTabbedviewDictStorage, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(
            Builder("dossier")
            .titled(u"Testd\xf6ssier XY")
            .within(self.repo_folder))

        self.document = create(Builder("document").within(self.dossier))

    def test_call_storage_with_proxy_will_change_context_to_subview(self):
        proxy_view = self.document.restrictedTraverse(
            'tabbedview_view-documents-proxy')

        sub_view = self.document.restrictedTraverse(
            'tabbedview_view-documents')

        self.assertNotIsInstance(
            IDictStorage(sub_view).context, proxy_view.__class__)
        self.assertIsInstance(
            IDictStorage(sub_view).context, sub_view.__class__)

    def test_call_storage_with_subview_will_not_change_context(self):
        sub_view = self.document.restrictedTraverse(
            'tabbedview_view-documents')

        self.assertIsInstance(
            IDictStorage(sub_view).context, sub_view.__class__)
