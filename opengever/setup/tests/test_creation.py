from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.utils import ogds_service
from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile


class TestUnitCreation(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestUnitCreation, self).setUp()
        self.group = create(Builder('ogds_group').id('users'))
        applyProfile(self.portal, 'opengever.setup.tests:units')

    def test_admin_unit_created(self):
        self.assertEqual(1, len(ogds_service().all_admin_units()))
        admin_unit = ogds_service().fetch_admin_unit('admin')
        self.assertIsNotNone(admin_unit)

    def test_org_unit_created(self):
        self.assertEqual(1, len(ogds_service().all_org_units()))
        org_unit = ogds_service().fetch_org_unit('org')
        self.assertIsNotNone(org_unit)
        self.assertIsNotNone(org_unit.admin_unit)
        self.assertEqual(self.group, org_unit.users_group())
        self.assertEqual(self.group, org_unit.inbox_group())
