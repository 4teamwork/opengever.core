from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestGetCurrentOrgUnit(IntegrationTestCase):

    def setUp(self):
        super(TestGetCurrentOrgUnit, self).setUp()
        registry = getUtility(IRegistry)
        self.au_config = registry.forInterface(IAdminUnitConfiguration)

    def test_get_current_admin_unit_returns_unit_configured_in_registry(self):
        unit_id = self.au_config.current_unit_id
        self.assertEqual('plone', unit_id)

        self.assertEqual(
            ogds_service().fetch_admin_unit(unit_id),
            get_current_admin_unit())

    def test_get_current_admin_unit_returns_none_if_unit_not_configured(self):
        self.au_config.current_unit_id = None

        self.assertEqual(None, get_current_admin_unit())
