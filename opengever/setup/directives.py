from opengever.setup.interfaces import IClientConfigurationRegistry
from opengever.setup.registry import ClientConfigurationRegistry
from zope.component import queryUtility, provideUtility


class ClientDirective(object):

    def __call__(self, *args, **kwargs):
        registry = queryUtility(IClientConfigurationRegistry)
        if registry is None:
            registry = ClientConfigurationRegistry()
            provideUtility(registry)

        registry.update_clients(args[0], kwargs)


client_directive = ClientDirective()


class PolicyDirective(object):

    def __call__(self, *args, **kwargs):
        registry = queryUtility(IClientConfigurationRegistry)
        if registry is None:
            registry = ClientConfigurationRegistry()
            provideUtility(registry)

        if kwargs.get('additional_profiles'):
            kwargs['additional_profiles'] = self.get_stripped_list(
                kwargs.get('additional_profiles'))

        if kwargs.get('client_ids'):
            kwargs['client_ids'] = self.get_stripped_list(
                kwargs.get('client_ids'))

        registry.update_policy(args[0], kwargs)

    def get_stripped_list(self, value):
        return [item.strip() for item in value.split(',')]


policy_directive = PolicyDirective()
