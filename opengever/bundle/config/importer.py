from opengever.base.casauth import build_cas_server_url
from opengever.ogds.auth.admin_unit import addAdminUnitAuthenticationPlugin
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from opengever.setup.deploy import POLICYLESS_SITE_ID
from plone import api
from plone.registry.interfaces import IRegistry
from StringIO import StringIO
from zope.component import getUtility
import json
import logging


log = logging.getLogger('opengever.bundle')
log.setLevel(logging.INFO)


class ConfigImportException(Exception):
    pass


class ConfigImporter(object):

    def __init__(self, json_data, allow_skip_units=False):
        self.configuration = json_data
        self.allow_skip_units = allow_skip_units
        self.portal = api.portal.get()

    def run(self, development_mode=False):
        self.development_mode = development_mode
        self.import_units()
        self.update_casauth_settings()
        self.install_admin_unit_auth_plugin()
        self.import_registry_settings()
        return True

    def import_units(self):
        units_config = self.configuration['units']
        self.create_admin_units(units_config)
        self.create_org_units(units_config)

    def create_admin_units(self, units_config):
        admin_units = units_config['admin_units']
        assert len(admin_units) == 1
        admin_unit_id = admin_units[0]['unit_id'].decode('utf-8')

        admin_units = StringIO(json.dumps(admin_units))
        AdminUnitCreator(
            is_development=self.development_mode,
            is_policyless=True,
            skip_if_exists=self.allow_skip_units).run(admin_units)

        api.portal.set_registry_record(
            'current_unit_id', admin_unit_id,
            interface=IAdminUnitConfiguration)

    def create_org_units(self, units_config):
        org_units = units_config['org_units']
        org_units = StringIO(json.dumps(org_units))
        OrgUnitCreator(
            is_development=self.development_mode,
            is_policyless=True,
            skip_if_exists=self.allow_skip_units).run(org_units)

    def update_casauth_settings(self):
        """Update cas_auth plugin settings now that the admin unit exists.

        Because the cas_auth plugin was installed during Plone site creation
        when no admin unit exists yet in policyless mode, its configuration
        needs updating.
        """
        au = get_current_admin_unit()
        if au.public_url == 'http://localhost:8080/%s' % POLICYLESS_SITE_ID:
            # Local development - no rewrite rules, use local Ianus
            cas_server_url = 'http://localhost:8081/cas'
        else:
            # Update placeholder URL with real one based on admin unit
            cas_server_url = build_cas_server_url('portal/cas')

        self.portal.acl_users.cas_auth._cas_server_url = cas_server_url

        # Rename session cookie
        # During Plone site creation, this will have been suffixed with the
        # Plone site ID. Because that's going to be the same for every
        # deployment in a multi-admin-unit policyless cluster, we rename it
        # (again) to suffix it with the admin unit ID, which would be unique.
        plugin = api.portal.get_tool('acl_users')['session']
        plugin.manage_changeProperties({
            'cookie_name': '__ac_' + au.id().replace('-', '_'),
        })

    def install_admin_unit_auth_plugin(self):
        addAdminUnitAuthenticationPlugin(
            None, 'admin_unit_auth', 'Admin Unit Authentication Plugin')

    def import_registry_settings(self):
        registry = getUtility(IRegistry)

        settings_to_import = self.configuration.get('registry', {})
        for key, value in sorted(settings_to_import.items()):
            # TODO: Might need to do some typecasting for some field types
            record = registry.records[key]
            record.field.validate(value)
            record.value = value
            log.info('Set registry record %r to %r' % (key, value))
