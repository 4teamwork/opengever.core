from ftw.upgrade import UpgradeStep
from opengever.webactions.interfaces import IWebActionsStorage
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


class InitializeWebActionsStorage(UpgradeStep):
    """Initialize WebActionsStorage.
    """

    def __call__(self):
        # IWebActionsStorage.__init__() will initialize the storage
        getMultiAdapter((getSite(), getRequest()), IWebActionsStorage)
