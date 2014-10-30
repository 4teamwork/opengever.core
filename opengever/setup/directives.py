from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import ILDAPConfigurationRegistry
from opengever.setup.registry import DeploymentConfigurationRegistry
from opengever.setup.registry import LDAPConfigurationRegistry
from zope.component import provideUtility
from zope.component import queryUtility


class DeploymentDirective(object):

    def __call__(self, *args, **kwargs):
        registry = queryUtility(IDeploymentConfigurationRegistry)
        if registry is None:
            registry = DeploymentConfigurationRegistry()
            provideUtility(registry)

        if kwargs.get('additional_profiles'):
            kwargs['additional_profiles'] = self.get_stripped_list(
                kwargs.get('additional_profiles'))

        registry.update_deployments(args[0], kwargs)

    def get_stripped_list(self, value):
        return [item.strip() for item in value.split(',')]

deployment_directive = DeploymentDirective()


class LDAPDirective(object):

    def __call__(self, *args, **kwargs):
        registry = queryUtility(ILDAPConfigurationRegistry)
        if registry is None:
            registry = LDAPConfigurationRegistry()
            provideUtility(registry)
        registry.update_ldaps(args[0], kwargs)

ldap_directive = LDAPDirective()
