from ftw.upgrade import UpgradeStep
from opengever.mail.interfaces import ISendDocumentConf
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class AddRegistryEntries(UpgradeStep):

    def __call__(self):
        self.update_registry_entries([ISendDocumentConf, ])

    # TODO: could maybe moved to ftw.upgrade
    # as an default upgradestep helper method
    def update_registry_entries(self, interfaces):
        registry = getUtility(IRegistry)
        # update the registry entries
        for interface in interfaces:
            registry.registerInterface(interface)
