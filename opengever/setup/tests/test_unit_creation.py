from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.utils import ogds_service
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

    @property
    def data_with_all_required_attrs(self):
        return {
            'unit_id': 'foo',
            'admin_unit_id': 'bar',
            'users_group_id': 'users',
            'inbox_group_id': 'users',
        }

    def create_org_unit_for(self, data):
        OrgUnitCreator().run(self.as_file(data))

    def test_fails_when_client_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['unit_id']
        self.assertRaises(GeverSetupException, self.create_org_unit_for, data)

    def test_fails_when_admin_unit_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['admin_unit_id']
        self.assertRaises(GeverSetupException, self.create_org_unit_for, data)

    def test_fails_when_uses_group_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['users_group_id']
        self.assertRaises(GeverSetupException, self.create_org_unit_for, data)

    def test_fails_when_inbox_group_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['inbox_group_id']
        self.assertRaises(GeverSetupException, self.create_org_unit_for, data)

    def test_fails_when_admin_unit_does_not_exist(self):
        create(Builder('ogds_group').id('users'))

        data = self.data_with_all_required_attrs
        self.assertRaises(GeverSetupException, self.create_org_unit_for, data)

    def test_fails_when_group_does_not_exist(self):
        create(Builder('admin_unit').id('bar'))

        data = self.data_with_all_required_attrs
        self.assertRaises(GeverSetupException, self.create_org_unit_for, data)

    def test_attributes_are_set(self):
        create(Builder('admin_unit').id('admin'))
        create(Builder('ogds_group').id('users'))

        attributes = {
            "unit_id": 'org',
            "title": "My cool new org unit",
            "enabled": False,
            "ip_address": "1.2.3.4",
            "site_url": "http://example.com",
            "public_url": "http://example.com/public",
            "admin_unit_id": "admin",
            'users_group_id': 'users',
            'inbox_group_id': 'users',
        }
        self.create_org_unit_for([attributes])
        client = self.service.fetch_org_unit('org')._client

        attributes['client_id'] = attributes['unit_id']
        del attributes['unit_id']

        for attribute, value in attributes.items():
            self.assertEqual(value, getattr(client, attribute),
                             "invalid: '{}'".format(attribute))
