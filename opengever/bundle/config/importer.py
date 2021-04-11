from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from opengever.setup.ldap_creds import get_ldap_credentials
from opengever.setup.ldap_creds import update_credentials
from plone import api
from plone.registry.interfaces import IRegistry
from StringIO import StringIO
from zope.component import getUtility
from ZPublisher.HTTPRequest import default_encoding
import json
import logging
import os


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
        self.import_ldap_settings()
        self.import_units()
        self.import_registry_settings()
        return True

    def import_ldap_settings(self):
        LDAPSettingsImporter(self.portal, self.configuration).run()

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

    def import_registry_settings(self):
        registry = getUtility(IRegistry)

        settings_to_import = self.configuration.get('registry', {})
        for key, value in sorted(settings_to_import.items()):
            # TODO: Might need to do some typecasting for some field types
            record = registry.records[key]
            record.field.validate(value)
            record.value = value
            log.info('Set registry record %r to %r' % (key, value))


class LDAPSettingsImporter(object):

    SUPPORTED_PROPERTIES = (
        'users_base',
        'groups_base',
        '_binduid',
        '_bindpwd',
        'servers',
    )

    PLUGIN_ID = 'ldap'

    def __init__(self, portal, configuration):
        self.portal = portal
        self.configuration = configuration

    def run(self):
        """Import LDAP settings from bundle configuration.json.

        Loosely based on Products.LDAPUserFolder.exportimport.
        """
        ldap_config = self.configuration['ldap']
        uf = self.get_ldap_user_folder()

        for key, value in ldap_config.items():

            if key == 'servers':
                servers = value
                if len(servers) > 1:
                    raise ConfigImportException(
                        'Import of multiple servers not supported yet')

                server = servers[0]

                host = server['host']
                protocol = server.get('protocol', 'ldap')
                port = int(server.get('port', 389))
                conn_timeout = int(server.get('conn_timeout', 5))
                op_timeout = int(server.get('op_timeout', -1))

                if protocol.lower() == 'ldaps':
                    use_ssl = 1
                elif protocol.lower() == 'ldapi':
                    use_ssl = 2
                else:
                    use_ssl = 0

                uf.manage_addServer(
                    host.encode(default_encoding),
                    port=port,
                    use_ssl=use_ssl,
                    conn_timeout=conn_timeout,
                    op_timeout=op_timeout,
                )

                self.configure_bind_credentials(uf, ldap_config, host)
                continue

            if key not in self.SUPPORTED_PROPERTIES:
                raise ConfigImportException(
                    'LDAP property not supported: %r' % key)

            if key in ('_binduid', '_bindpwd'):
                continue

            uf._setProperty(key, value)

        sync_ogds(self.portal)

    def configure_bind_credentials(self, uf, ldap_config, host):
        """Determine and set LDAP credentials.

        Order of precedence:
        - Environment variables
        - ~/.opengever/ldap/<hostname>.json
        - configuration.json from Bundle
        """
        # Consume possible credentials from bundle config first.
        # Shouldn't be used in production, but it's here if we need it.
        _binduid = ldap_config.get('_binduid')
        _bindpwd = ldap_config.get('_bindpwd')

        # If present, override with credentials from ~/.opengever/ldap
        creds_from_file = get_ldap_credentials(host)
        if creds_from_file:
            creds = creds_from_file[self.PLUGIN_ID]
            _binduid = creds['user'].encode('utf-8')
            _bindpwd = creds['password'].encode('utf-8')

        # Environment variables - highest precedence
        _binduid = os.environ.get('PLONE_LDAP_BIND_UID', _binduid)
        _bindpwd = os.environ.get('PLONE_LDAP_BIND_PWD', _bindpwd)

        if all([_binduid, _bindpwd]):
            update_credentials(uf, _binduid, _bindpwd)

    def get_ldap_user_folder(self):
        if self.PLUGIN_ID not in self.portal.acl_users:
            raise ConfigImportException(
                "LDAP Plugin not found. An LDAP plugin with ID %r must "
                "exist to import LDAP settings via bundle." % self.PLUGIN_ID)
        return self.portal.acl_users.ldap.acl_users
