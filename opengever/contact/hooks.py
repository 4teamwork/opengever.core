from opengever.contact.config import INDEXES
from Products.CMFCore.utils import getToolByName
import logging


def add_catalog_indexes(context):
    logger = logging.getLogger('opengever.contact')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    indexables = []
    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def installed(site):
    add_catalog_indexes(site)
