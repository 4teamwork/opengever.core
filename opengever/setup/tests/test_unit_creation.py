from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.service import ogds_service
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from opengever.setup.exception import GeverSetupException
from opengever.testing import FunctionalTestCase
from StringIO import StringIO
import json


class BaseTestUnitCreator(FunctionalTestCase):

    def setUp(self):
        super(BaseTestUnitCreator, self).setUp()
        self.service = ogds_service()

    def as_file(self, data):
        return StringIO(json.dumps(data))


class TestAdminUnitCreator(BaseTestUnitCreator):

    def create_admin_unit_for(self, data):
        AdminUnitCreator().run(self.as_file(data))

    @property
    def data_with_all_required_attrs(self):
        return {
            "unit_id": "admin",
            "ip_address": "1.2.3.4",
            "site_url": "http://example.com",
            "public_url": "http://example.com/public",
        }

    def test_unit_id_required(self):
        data = self.data_with_all_required_attrs
        del data['unit_id']
        with self.assertRaises(GeverSetupException):
            self.create_admin_unit_for(data)

    def test_ip_address_required(self):
        data = self.data_with_all_required_attrs
        del data['ip_address']
        with self.assertRaises(GeverSetupException):
            self.create_admin_unit_for(data)

    def test_site_url_required(self):
        data = self.data_with_all_required_attrs
        del data['site_url']
        with self.assertRaises(GeverSetupException):
            self.create_admin_unit_for(data)

    def test_public_url_required(self):
        data = self.data_with_all_required_attrs
        del data['public_url']
        with self.assertRaises(GeverSetupException):
            self.create_admin_unit_for(data)

    def test_attributes_are_set(self):
        attributes = {
            "unit_id": 'admin',
            "title": "My cool new admin unit",
            "enabled": False,
            "ip_address": "1.2.3.4",
            "site_url": "http://example.com",
            "public_url": "http://example.com/public",
            "abbreviation": "adm"
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

    def test_fails_when_unit_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['unit_id']
        with self.assertRaises(GeverSetupException):
            self.create_org_unit_for(data)

    def test_fails_when_admin_unit_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['admin_unit_id']
        with self.assertRaises(GeverSetupException):
            self.create_org_unit_for(data)

    def test_fails_when_uses_group_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['users_group_id']
        with self.assertRaises(GeverSetupException):
            self.create_org_unit_for(data)

    def test_fails_when_inbox_group_id_is_not_specified(self):
        data = self.data_with_all_required_attrs
        del data['inbox_group_id']
        with self.assertRaises(GeverSetupException):
            self.create_org_unit_for(data)

    def test_fails_when_admin_unit_does_not_exist(self):
        create(Builder('ogds_group').id('users'))

        data = self.data_with_all_required_attrs
        with self.assertRaises(GeverSetupException):
            self.create_org_unit_for(data)

    def test_fails_when_group_does_not_exist(self):
        create(Builder('admin_unit').id('bar'))

        data = self.data_with_all_required_attrs
        with self.assertRaises(GeverSetupException):
            self.create_org_unit_for(data)

    def test_assignes_users_group_to_member_role(self):
        create(Builder('admin_unit').id('bar'))
        create(Builder('ogds_group').id('users'))

        self.create_org_unit_for([self.data_with_all_required_attrs])
        role_manager = self.portal.acl_users.portal_role_manager
        assigned_principal_ids = [
            each[0] for each in role_manager.listAssignedPrincipals('Member')]
        self.assertIn('users', assigned_principal_ids)

    def test_attributes_are_set(self):
        create(Builder('admin_unit').id('admin'))
        create(Builder('ogds_group').id('users'))

        attributes = {
            "unit_id": 'org',
            "title": "My cool new org unit",
            "enabled": False,
            "admin_unit_id": "admin",
            'users_group_id': 'users',
            'inbox_group_id': 'users',
        }
        self.create_org_unit_for([attributes])
        org_unit = self.service.fetch_org_unit('org')

        for attribute, value in attributes.items():
            self.assertEqual(value, getattr(org_unit, attribute),
                             "invalid: '{}'".format(attribute))
