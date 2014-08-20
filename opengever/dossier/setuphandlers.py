import logging
from opengever.dossier.config import INDEXES
from opengever.core.catalog import add_catalog_indexes


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    if context.readDataFile('opengever.dossier_indexes.txt') is None:
        return

    add_catalog_indexes(INDEXES, logging.getLogger('opengever.dossier'))
