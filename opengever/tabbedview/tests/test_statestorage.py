from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.tabbedview.interfaces import ITabbedViewProxy
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter


class TestGeverGridStateStorageKeyGenerator(FunctionalTestCase):

    def test_get_key_returns_proxy_view_without_postfix(self):
        view = self.portal.restrictedTraverse('tabbedview_view-mydocuments-proxy')

        self.assertTrue(ITabbedViewProxy.providedBy(view))

        generator = getMultiAdapter((self.portal, view, self.request),
                                    IGridStateStorageKeyGenerator)

        self.assertEqual(
            'ftw.tabbedview-Plone Site-tabbedview_view-mydocuments-test_user_1_',
            generator.get_key())
