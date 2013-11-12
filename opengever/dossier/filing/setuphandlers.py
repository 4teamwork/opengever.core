from Products.CMFCore.utils import getToolByName
import logging


PROFILE_ID = 'profile-opengever.dossier:filing'
logger = logging.getLogger('opengever.dossier')


def add_catalog_indexes(context):

    # Run the catalog.xml step to set the defined new metadata
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    # Specify the indexes you want, with ('index_name', 'index_type', 'args')
    wanted = (('filing_no', 'FieldIndex', {}),
              ('searchable_filing_no', 'ZCTextIndex',
               {'index_type': 'Okapi BM25 Rank',
                'lexicon_id': 'plone_lexicon'}),)

    indexables = []
    for name, meta_type, args in wanted:
        if name not in indexes:
            if meta_type == 'ZCTextIndex':
                class Extras:
                    def __init__(self, **kwargs):
                        for key, value in kwargs.items():
                            setattr(self, key, value)
                catalog.addIndex(name, meta_type, Extras(**args))
            else:
                catalog.addIndex(name, meta_type)

            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)

    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    if context.readDataFile('opengever.filing_indexes.txt') is None:
        return
    site = context.getSite()
    add_catalog_indexes(site)
