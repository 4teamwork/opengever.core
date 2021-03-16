from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.setup.creation.adminunit import AdminUnitCreator
from opengever.setup.creation.orgunit import OrgUnitCreator
from plone import api
from plone.registry.interfaces import IRegistry
from StringIO import StringIO
from zope.component import getUtility
import json
import logging


log = logging.getLogger('opengever.bundle')
log.setLevel(logging.INFO)


class ConfigImporter(object):

    def __init__(self, json_data, allow_skip_units=False):
        self.configuration = json_data
        self.allow_skip_units = allow_skip_units

    def run(self, development_mode=False):
        self.development_mode = development_mode
        self.import_units()
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

    def import_registry_settings(self):
        registry = getUtility(IRegistry)

        settings_to_import = self.configuration.get('registry', {})
        for key, value in sorted(settings_to_import.items()):
            # TODO: Might need to do some typecasting for some field types
            record = registry.records[key]
            record.field.validate(value)
            record.value = value
            log.info('Set registry record %r to %r' % (key, value))
