from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger
import logging


logger = logging.getLogger('ftw.upgrade')


ZCTEXT_INDEXES_TO_REMOVE = [
    'document_author',
    'SearchableText',
]

INDEXES_TO_REMOVE = [
    'total_comments',
]


class EnsureSolrOnlyIndicesDroppedFromCatalog(UpgradeStep):
    """Ensure solr only indices dropped from catalog.

    We seem to have different indexes still around for different deployments.
    The following states exist:

    - Neither `document_author` nor `SearchableText`:
      This happened when solr was activated with the `activate_solr.py` script
      from `opengever.maintenance`. It deleted the `document_author` index
      which was still present in `opengever.core`.

    - Only `document_author`:
      This is the state for all new deployments where `activate_solr.py` has
      not been run as the `document_author` index was still present in
      `opengever.core`.

    - Indices `document_author`, `SearchableText` and `total_comments`:
      The upgrade step to delete indices was faulty and did not correctly
      remove `SearchableText` and `total_comments` due to a missing comma.

    This upgrade makes sure that the remaining indices are dropped
    consistently for all deployments. It also conditionally clears the lexicon
    and rebuilds the remaining ZCTextIndex indices to ensure minimal catalog
    size.

    Note that the `document_author` metadata is left in place as it is still
    used by the `ILaTexListing` for documents.
    """
    deferrable = True

    def __call__(self):
        self.found_zctext_index_to_remove = False
        self.remove_indexes()
        self.reindex_zc_text_indices()

    def remove_indexes(self):
        catalog = self.getToolByName('portal_catalog')
        for index in ZCTEXT_INDEXES_TO_REMOVE:
            if index in catalog._catalog.indexes:
                self.found_zctext_index_to_remove = True
                catalog._catalog.delIndex(index)
                logger.info('Removed catalog index {}.'.format(index))
        for index in INDEXES_TO_REMOVE:
            if index in catalog._catalog.indexes:
                catalog._catalog.delIndex(index)
                logger.info('Removed catalog index {}.'.format(index))

    def reindex_zc_text_indices(self):
        if not self.found_zctext_index_to_remove:
            return

        catalog = self.getToolByName('portal_catalog')

        title_index = catalog._catalog.getIndex('Title')
        catalog.clearIndex('Title')
        logger.info('Cleared Title index.')

        if 'searchable_filing_no' in catalog._catalog.indexes:
            searchable_filing_no_index = catalog._catalog.getIndex(
                'searchable_filing_no')
            catalog.clearIndex('searchable_filing_no')
            logger.info('Cleared searchable_filing_no index.')
        else:
            searchable_filing_no_index = None

        lexicon = catalog['plone_lexicon']
        lexicon.clear()
        logger.info('Cleared plone_lexicon.')

        items = catalog.unrestrictedSearchResults()
        for item in ProgressLogger('Reindexing ZCTextIndex indices.', items):
            title_index.index_object(item.getRID(), item)
            if searchable_filing_no_index:
                searchable_filing_no_index.index_object(item.getRID(), item)
