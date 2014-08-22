from opengever.core.catalog import add_catalog_indexes
from opengever.document.config import INDEXES
import logging


def installed(site):
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.document'))
