from ftw.upgrade import UpgradeStep
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


TITLE_FIELD = 'opengever.base.interfaces.IBaseClientID.client_title'
ID_FIELD = 'opengever.base.interfaces.IBaseClientID.client_id'


class InitalizeClientTitleRegistryEntry(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.base.upgrades:2602')

        self.initialize()

    def initialize(self):
        """For exisiting clients we will use the client_id as client_title
        as default."""
        registry = getUtility(IRegistry)

        if not registry.get(TITLE_FIELD, None):
            registry[TITLE_FIELD] = registry.get(ID_FIELD)
