from opengever.contact.config import INDEXES
from opengever.core.catalog import add_catalog_indexes
import logging


def installed(site):
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.contact'))
