from opengever.core.catalog import add_catalog_indexes
from opengever.document.config import INDEXES
import logging


def import_various(context):
    if context.readDataFile('opengever.document_indexes.txt') is None:
        return

    add_catalog_indexes(INDEXES, logging.getLogger('opengever.document'))
