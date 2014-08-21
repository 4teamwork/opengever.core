import logging
from opengever.core.catalog import add_catalog_indexes
from opengever.mail.config import INDEXES


def installed(site):
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.mail'))
