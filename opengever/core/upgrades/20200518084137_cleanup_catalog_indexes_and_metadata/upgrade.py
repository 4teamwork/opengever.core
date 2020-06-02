from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep


INDEXES_TO_REMOVE = [
    'assigned_client',
    'client_id',
    'commentators',
    'Date',
    'Description',
    'effective',
    'effectiveRange',
    'expires',
    'getRawRelatedItems',
    'in_reply_to',
    'meta_type',
    'SearchableText'
    'total_comments',
]

METADATA_TO_REMOVE = [
    'assigned_client',
    'author_name',
    'commentators',
    'CreationDate',
    'Date',
    'effective',
    'EffectiveDate',
    'ExpirationDate',
    'expires',
    'getObjSize',
    'getRemoteUrl',
    'last_comment_date',
    'location',
    'meta_type',
    'ModificationDate',
    'total_comments',
]


class CleanupCatalogIndexesAndMetadata(UpgradeStep):
    """Cleanup catalog indexes and metadata.
    """

    deferrable = True

    def __call__(self):
        self.remove_indexes()
        self.remove_metadata()

    def remove_indexes(self):
        catalog = self.getToolByName('portal_catalog')
        for index in INDEXES_TO_REMOVE:
            if index in catalog._catalog.indexes:
                catalog._catalog.delIndex(index)

    def remove_metadata(self):
        catalog = self.getToolByName('portal_catalog')
        schema = catalog._catalog.schema
        names = list(catalog._catalog.names)
        del_indexes = []
        del_column_numbers = []
        for column in METADATA_TO_REMOVE:
            if column in names and column in schema:
                del_indexes.append(names.index(column))
                del_column_numbers.append(schema[column])

        # Remove columns from names
        del_indexes.sort(reverse=True)
        for del_index in del_indexes:
            del names[del_index]

        # Rebuild the schema
        schema = {}
        for i, name in enumerate(names):
            schema[name] = i

        catalog._catalog.schema = schema
        catalog._catalog.names = tuple(names)

        catalog._catalog.updateBrains()

        # Remove the column values from each record
        del_column_numbers.sort(reverse=True)
        for key, value in ProgressLogger(
            'Remove catalog metadata', catalog._catalog.data.items()
        ):
            for column_number in del_column_numbers:
                value = value[:column_number] + value[column_number + 1:]
            catalog._catalog.data[key] = value
