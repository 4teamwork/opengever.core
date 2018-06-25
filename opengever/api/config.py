from opengever.base.interfaces import IGeverSettings
from plone.restapi.services import Service


class Config(Service):
    """GEVER configuration"""

    def reply(self):
        return IGeverSettings(self.context).get_config()

    def check_permission(self):
        return
