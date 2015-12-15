from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile


class TestGeverStateView(FunctionalTestCase):

    def setUp(self):
        super(TestGeverStateView, self).setUp()
        get_current_admin_unit().public_url = 'http://foo.org/cluster'

    def test_cluster_base_url(self):
        self.assertEquals(
            'http://foo.org/cluster/',
            self.portal.restrictedTraverse('@@gever_state/cluster_base_url')(),
        )

    def test_gever_portal_url(self):
        self.assertEquals(
            'http://foo.org/cluster/portal',
            self.portal.restrictedTraverse('@@gever_state/gever_portal_url')(),
        )

    def test_cas_server_url(self):
        applyProfile(self.portal, 'opengever.setup:casauth')
        self.assertEquals(
            'http://foo.org/cluster/portal',
            self.portal.restrictedTraverse('@@gever_state/cas_server_url')(),
        )
