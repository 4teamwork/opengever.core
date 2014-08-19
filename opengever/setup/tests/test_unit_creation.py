from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from opengever.setup.exception import GeverSetupException
from opengever.testing import MEMORY_DB_LAYER
from StringIO import StringIO
from unittest import TestCase
import json


class BaseTestUnitCreator(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(BaseTestUnitCreator, self).setUp()
        self.service = ogds_service()
        self.session = self.layer.session

    def as_file(self, data):
        return StringIO(json.dumps(data))


class TestAdminUnitCreator(BaseTestUnitCreator):

    def create_admin_unit_for(self, data):
        AdminUnitCreator().run(self.as_file(data))

    def test_unit_id_required(self):
        self.assertRaises(
            GeverSetupException,
            self.create_admin_unit_for,
            [
                {
                    "title": "My cool new admin unit"
                }
            ],
        )

    def test_attributes_are_set(self):
        attributes = {
            "unit_id": 'admin',
            "title": "My cool new admin unit",
            "enabled": False,
            "ip_address": "1.2.3.4",
            "site_url": "http://example.com",
            "public_url": "http://example.com/public"
        }
        self.create_admin_unit_for([attributes])
        admin_unit = self.service.fetch_admin_unit('admin')

        for attribute, value in attributes.items():
            self.assertEqual(value, getattr(admin_unit, attribute),
                             "invalid: '{}'".format(attribute))


class TestOrgUnitCreator(BaseTestUnitCreator):

    def create_org_unit_for(self, data):
        OrgUnitCreator().run(self.as_file(data))

    def test_client_id_required(self):
        self.assertRaises(
            GeverSetupException,
            self.create_org_unit_for,
            [
                {
                    "title": "My cool new admin unit",
                    "admin_unit_id": "foo"
                }
            ],
        )

    def test_admin_unit_id_required(self):
        self.assertRaises(
            GeverSetupException,
            self.create_org_unit_for,
            [
                {
                    "client_id": "foo",
                    "title": "My cool new admin unit"
                }
            ],
        )

    def test_admin_unit_required(self):
        self.assertRaises(
            GeverSetupException,
            self.create_org_unit_for,
            [
                {
                    "client_id": "foo",
                    "title": "My cool new admin unit",
                    "admin_unit_id": "foo"
                }
            ],
        )

    def test_attributes_are_set(self):
        self.session.add(AdminUnit(unit_id="admin"))
        attributes = {
            "client_id": 'org',
            "title": "My cool new org unit",
            "enabled": False,
            "ip_address": "1.2.3.4",
            "site_url": "http://example.com",
            "public_url": "http://example.com/public",
            "admin_unit_id": "admin"
        }
        self.create_org_unit_for([attributes])
        client = self.service.fetch_org_unit('org')._client

        for attribute, value in attributes.items():
            self.assertEqual(value, getattr(client, attribute),
                             "invalid: '{}'".format(attribute))

