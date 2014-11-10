from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import ILDAPConfigurationRegistry
from zope.interface import implements


class BaseConfigurationRegistry(object):
    """A configuration registry contains configuration dictionaries.
    """

    def __init__(self):
        self.configs = {}

    def _update_entries(self, title, config_dict):
        if title in self.configs:
            self.configs[title].update(config_dict)
        else:
            self.configs[title] = config_dict

    def _list_entries(self):
        results = []
        for key, values in self.configs.items():
            if values['is_default']:
                results.insert(0, key)
            else:
                results.append(key)
        return results

    def _get_entry(self, title):
        return self.configs.get(title)


class DeploymentConfigurationRegistry(BaseConfigurationRegistry):
    implements(IDeploymentConfigurationRegistry)

    def update_deployments(self, title, config_dict):
        self._update_entries(title, config_dict)

    def list_deployments(self):
        return self._list_entries()

    def get_deployment(self, title):
        return self._get_entry(title)


class LDAPConfigurationRegistry(BaseConfigurationRegistry):
    implements(ILDAPConfigurationRegistry)

    def update_ldaps(self, title, config_dict):
        self._update_entries(title, config_dict)

    def list_ldaps(self):
        for key in self._list_entries():
            yield (key, self.get_ldap(key)['ldap_profile'])

    def get_ldap(self, title):
        return self._get_entry(title)
