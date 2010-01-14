from Products.CMFCore.utils import getToolByName
import logging
# The profile id of your package:
PROFILE_ID = 'profile-opengever.document:default'

def setup_versioning(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('opengever.document_versioning.txt') is None:
        return

    portal = context.getSite()

    # enable manual versioning for Document type
    types = [
        'opengever.document.document',
        ]
    pr = getToolByName(portal, 'portal_repository')
    for type in types:
        pr._versionable_content_types.append(type)
        pr._version_policy_mapping[type] = [
            'version_on_revert',
            ]


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('opengever.document')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (
            ('delivery_date', 'DateIndex'),
            ('document_author', 'FieldIndex'),
            ('checked_out', 'FieldIndex'),
            ('document_date', 'DateIndex'),
            ('receipt_date', 'DateIndex'),
            ('related_items', 'KeywordIndex'),
              )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    if context.readDataFile('opengever.document_indexes.txt') is None:
        return
    logger = context.getLogger('opengever.document')
    site = context.getSite()
    add_catalog_indexes(site, logger)