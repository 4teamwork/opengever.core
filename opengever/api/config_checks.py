from opengever.base.config_checks.manager import ConfigCheckManager
from plone.restapi.services import Service


class ConfigChecks(Service):
    """GEVER configuration checks"""

    def reply(self):
        errors = ConfigCheckManager().check_all()
        return {
            '@id': '{}/@config-checks'.format(self.context.absolute_url()),
            'errors': errors,
        }
