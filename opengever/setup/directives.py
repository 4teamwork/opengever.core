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

        title = args[0]
        registry.update_deployments(title, kwargs)

deployment_directive = DeploymentDirective()


class LDAPDirective(object):

    def __call__(self, *args, **kwargs):
        registry = queryUtility(ILDAPConfigurationRegistry)
        if registry is None:
            registry = LDAPConfigurationRegistry()
            provideUtility(registry)

        title = args[0]
        registry.update_ldaps(title, kwargs)

ldap_directive = LDAPDirective()
