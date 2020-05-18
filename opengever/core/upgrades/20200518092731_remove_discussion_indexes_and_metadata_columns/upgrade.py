from ftw.upgrade import UpgradeStep
from plone import api


class RemoveDiscussionIndexesAndMetadataColumns(UpgradeStep):
    """Remove discussion indexes and metadata columns.
    """

    def __call__(self):
        indexes = [
            'client_id',
            'commentators',
            'total_comments',
            'in_reply_to',
            'getRemoteUrl',
            'getRawRelatedItems',
            'meta_type',
        ]
        columns = [
            'commentators',
            'last_comment_date',
            'total_comments',
            'meta_type',
        ]

        for index in indexes:
            self.catalog_remove_index(index)

        catalog = api.portal.get_tool('portal_catalog')
        for column in columns:
            if column in catalog.schema():
                catalog.delColumn(column)
