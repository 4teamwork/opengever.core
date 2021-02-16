from ftw.bumblebee.config import bumblebee_config
from opengever.base import utils
from opengever.base.colorization import get_color
from opengever.base.interfaces import IGeverSettings
from opengever.inbox.utils import get_current_inbox
from opengever.officeconnector.helpers import is_client_ip_in_office_connector_disallowed_ip_ranges
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.service import ogds_service
from opengever.private import get_private_folder_url
from plone.restapi.services import Service


class ConfigGet(Service):
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

        - is_admin: If the current user is a GEVER Admin or not
        - bumblebee_app_id: The Bumblebee app id as configured in Plone (a string).

        - private_folder_url: The url to the private folder of the current
          user (a string). If the value is `None`, the user does not have
          a private folder or the feature is disabled in Plone.
        """
        config['is_emm_environment'] = is_client_ip_in_office_connector_disallowed_ip_ranges()
        config['is_admin'] = utils.is_administrator()
        config['bumblebee_app_id'] = bumblebee_config.app_id
        config['private_folder_url'] = get_private_folder_url()
        config['gever_colorization'] = get_color()

        plone_inbox = get_current_inbox(self.context)
        config['inbox_folder_url'] = plone_inbox.absolute_url() if plone_inbox else ''

        ogds_inbox = get_current_org_unit().inbox()
        current_user = ogds_service().fetch_current_user()
        config['is_inbox_user'] = current_user in ogds_inbox.assigned_users()
