from opengever.core.catalog import add_catalog_indexes
from opengever.task.config import INDEXES
import logging


def installed(context):
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.task'))
