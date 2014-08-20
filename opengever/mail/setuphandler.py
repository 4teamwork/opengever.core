import logging
from opengever.core.catalog import add_catalog_indexes
from opengever.mail.config import INDEXES


def import_various(setup):
    """Import step for configuration that is not handled in xml files.
    """
    if setup.readDataFile('opengever.mail.txt') is None:
        return
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.mail'))
