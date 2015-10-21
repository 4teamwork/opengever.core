from ftw.upgrade import UpgradeStep
from plone import api


class RemoveRelatedItemsMetadata(UpgradeStep):
    """Remove leftover related_items catalog metadata.

    Index and column in catalog.xml has already been removed in an upgrade to
    2602 - but not the actual metadata column in the catalog.

    """
    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        if 'related_items' in catalog.schema():
            catalog.delColumn('related_items')
