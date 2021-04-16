from ftw.builder import Builder
from ftw.builder import create
from opengever.base.model import create_session
from opengever.ogds.models.service import ogds_service
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile
from StringIO import StringIO
import json


class TestUnitCreation(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestUnitCreation, self).setUp()
        create(Builder('ogds_group').id('users'))
        applyProfile(self.portal, 'opengever.setup.tests:units')
        self.session = create_session()

        self.au_data = StringIO(json.dumps([{
            'unit_id': 'admin',
            'title': 'AdminUnit',
            'ip_address': '127.0.0.1',
            'site_url': 'http://admin.local',
            'public_url': 'http://admin.local',
            'abbreviation': 'A',
        }]))

        self.ou_data = StringIO(json.dumps([{
            'unit_id': 'org',
            'title': 'OrgUnit',
            'admin_unit_id': 'admin',
            'users_group_id': 'users',
            'inbox_group_id': 'users',

        }]))

    def test_admin_unit_created(self):
        self.assertEqual(1, len(ogds_service().all_admin_units()))
        admin_unit = ogds_service().fetch_admin_unit('admin')
        self.assertIsNotNone(admin_unit)

    def test_org_unit_created(self):
        self.assertEqual(1, len(ogds_service().all_org_units()))
        org_unit = ogds_service().fetch_org_unit('org')
        self.assertIsNotNone(org_unit)
        self.assertIsNotNone(org_unit.admin_unit)
        self.assertIsNotNone(org_unit.users_group)
        self.assertIsNotNone(org_unit.inbox_group)

    def test_allows_skipping_of_already_existing_units(self):
        au_creator = AdminUnitCreator(skip_if_exists=True)
        au_creator.run(self.au_data)
        self.session.flush()

        ou_creator = OrgUnitCreator(skip_if_exists=True)
        ou_creator.run(self.ou_data)
        self.session.flush()
