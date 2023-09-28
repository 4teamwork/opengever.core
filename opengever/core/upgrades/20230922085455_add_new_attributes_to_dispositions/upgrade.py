from ftw.upgrade import UpgradeStep
from opengever.disposition.interfaces import IDisposition
from persistent.list import PersistentList
from Products.CMFPlone.utils import safe_hasattr


class AddNewAttributesToDispositions(UpgradeStep):
    """Add new attributes to dispositions.
    """

    def __call__(self):
        query = {'object_provides': IDisposition.__identifier__}
        for disposition in self.objects(query, "Add storage for new attributes on dispositions."):
            if not safe_hasattr(disposition, "_dossiers_with_missing_permissions"):
                disposition._dossiers_with_missing_permissions = PersistentList()
            if not safe_hasattr(disposition, "_dossiers_with_extra_permissions"):
                disposition._dossiers_with_extra_permissions = PersistentList()
