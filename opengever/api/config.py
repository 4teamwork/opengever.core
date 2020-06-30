from ftw.bumblebee.config import bumblebee_config
from opengever.base import utils
from opengever.base.interfaces import IGeverSettings
from opengever.officeconnector.helpers import is_client_ip_in_office_connector_disallowed_ip_ranges
from opengever.private import get_private_folder_url
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
        """
        Injects additional configuration information:

        - is_admin_menu_visible: Indication for the GEVER UI if it should display
          the menu item "Verwaltung" in the navigation drawer.

        - bumblebee_app_id: The Bumblebee app id as configured in Plone (a string).

        - private_folder_url: The url to the private folder of the current
          user (a string). If the value is `None`, the user does not have
          a private folder or the feature is disabled in Plone.
        """
        config['is_emm_environment'] = is_client_ip_in_office_connector_disallowed_ip_ranges()
        config['is_admin_menu_visible'] = utils.is_administrator()
        config['bumblebee_app_id'] = bumblebee_config.app_id
        config['private_folder_url'] = get_private_folder_url()
