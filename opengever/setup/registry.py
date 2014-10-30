from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from zope.interface import implements


class DeploymentConfigurationRegistry(object):
    implements(IDeploymentConfigurationRegistry)

    def __init__(self):
        self.deployments = {}

    def update_deployments(self, ident, attr):
        if id in self.deployments:
            self.deployments[ident].update(attr)
        else:
            self.deployments[ident] = attr

    def list_deployments(self):
        return self.deployments.keys()

    def get_deployment(self, ident):
        return self.deployments.get(ident)
