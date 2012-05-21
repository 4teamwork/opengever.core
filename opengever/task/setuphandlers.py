import logging
from Products.CMFCore.utils import getToolByName
# The profile id of your package:
PROFILE_ID = 'profile-opengever.task:default'


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
        logger = logging.getLogger('opengever.task')

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
    wanted = (('deadline', 'DateIndex'),
              ('date_of_completion', 'DateIndex'),
              ('responsible', 'FieldIndex'),
              ('issuer', 'FieldIndex'),
              ('task_type', 'FieldIndex'),
              ('assigned_client', "KeywordIndex"),
              ('client_id', "KeywordIndex"),
              ('sequence_number', 'FieldIndex'),
              ('is_subtask', 'FieldIndex'),
              ('predecessor', 'FieldIndex'),
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
    if context.readDataFile('opengever.task_indexes.txt') is None:
        return
    logger = context.getLogger('opengever.task')
    site = context.getSite()
    add_catalog_indexes(site, logger)
