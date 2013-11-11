from opengever.setup.interfaces import IClientConfigurationRegistry
from zope.interface import implements


class ClientConfigurationRegistry(object):
    implements(IClientConfigurationRegistry)

    def __init__(self):
        self.clients = {}
        self.policies = {}

    def update_clients(self, id, attr):
        if id in self.clients:
            self.clients[id].update(attr)
        else:
            self.clients[id] = attr

    def update_policy(self, id, kwargs):
        if id in self.policies:
            self.policies[id].update(kwargs)
        else:
            self.policies[id] = kwargs

    def get_configuration(self, id):
        return self.clients.get(id)

    def get_policy(self, id):
        configuration = self.policies.get(id).copy()
        configuration['clients'] = []

        if configuration.get('multi_clients'):
            return self.generate_multi_policies(configuration)

        for client_id in configuration.get('client_ids'):
            configuration['clients'].append(self.get_configuration(client_id))
        return configuration

    def generate_multi_policies(self, configuration):
        configuration['clients'] = []
        client_id = configuration.get('client_ids')[0]
        muster_configuration = self.get_configuration(client_id)

        for i in range(1, 11):
            client = muster_configuration.copy()
            for key, value in client.items():
                if isinstance(value, unicode):
                    client[key] = value.format(client_number=str(i))
            configuration['clients'].append(client)

        return configuration

    def get_policies(self):
        for policy_id in self.policies.keys():
            yield self.get_policy(policy_id)

    def list_policies(self):
        return self.policies.keys()
