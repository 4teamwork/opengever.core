from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import IBaseClientID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class InitalizeClientTitleRegistryEntry(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.base.upgrades:2602')

        self.initialize()

    def initialize(self):
        """For exisiting clients we will use the client_id as client_title
        as default."""

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)

        if not proxy.client_title:
            proxy.client_title = proxy.client_id
