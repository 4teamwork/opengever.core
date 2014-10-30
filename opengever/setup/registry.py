from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import ILDAPConfigurationRegistry
from zope.interface import implements


class BaseConfigurationRegistry(object):

    def __init__(self):
        self.configs = {}

    def _update_entries(self, ident, attr):
        if ident in self.configs:
            self.configs[ident].update(attr)
        else:
            self.configs[ident] = attr

    def _list_entries(self):
        results = []
        for key, values in self.configs.items():
            if values['is_default']:
                results.insert(0, key)
            else:
                results.append(key)
        return results

    def _get_entry(self, ident):
        return self.configs.get(ident)


class DeploymentConfigurationRegistry(BaseConfigurationRegistry):
    implements(IDeploymentConfigurationRegistry)

    def update_deployments(self, ident, attr):
        self._update_entries(ident, attr)

    def list_deployments(self):
        return self._list_entries()

    def get_deployment(self, ident):
        return self._get_entry(ident)


class LDAPConfigurationRegistry(BaseConfigurationRegistry):
    implements(ILDAPConfigurationRegistry)

    def update_ldaps(self, ident, attr):
        self._update_entries(ident, attr)

    def list_ldaps(self):
        for key in self._list_entries():
            yield (key, self.get_ldap(key)['ldap_profile'])

    def get_ldap(self, ident):
        return self._get_entry(ident)
