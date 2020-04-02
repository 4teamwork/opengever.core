from opengever.base.interfaces import IGeverSettings
from opengever.officeconnector.helpers import is_client_ip_in_office_connector_disallowed_ip_range
from plone.restapi.services import Service


class Config(Service):
    """GEVER configuration"""

    def reply(self):
        config = IGeverSettings(self.context).get_config()
        self.add_additional_infos(config)
        return config

    def check_permission(self):
        return

    def add_additional_infos(self, config):
        config['is_emm_environment'] = is_client_ip_in_office_connector_disallowed_ip_range()
