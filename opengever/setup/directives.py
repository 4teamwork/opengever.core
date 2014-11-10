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

        registry.update_deployments(args[0], kwargs)

deployment_directive = DeploymentDirective()


class LDAPDirective(object):

    def __call__(self, *args, **kwargs):
        registry = queryUtility(ILDAPConfigurationRegistry)
        if registry is None:
            registry = LDAPConfigurationRegistry()
            provideUtility(registry)
        registry.update_ldaps(args[0], kwargs)

ldap_directive = LDAPDirective()
