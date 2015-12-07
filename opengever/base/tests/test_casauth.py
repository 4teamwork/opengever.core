from opengever.base.casauth import get_cas_portal_url
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase


class TestCASPortalUrl(FunctionalTestCase):

    def test_is_adminunits_puplic_url_and_slash_portal(self):
        self.assertEquals('http://example.com/portal', get_cas_portal_url())

    def test_trailing_slashes_are_stripped(self):
        get_current_admin_unit().public_url = 'http://example.com/'
        self.assertEquals('http://example.com/portal', get_cas_portal_url())
