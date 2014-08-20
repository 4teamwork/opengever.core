from opengever.core.catalog import add_catalog_indexes
from opengever.task.config import INDEXES
import logging


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    if context.readDataFile('opengever.task_indexes.txt') is None:
        return

    add_catalog_indexes(INDEXES, logging.getLogger('opengever.task'))
