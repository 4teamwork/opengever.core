from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrSettings
from ftw.upgrade import UpgradeStep
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import logging


logger = logging.getLogger('opengever.core')


class FixDocsOnlyPartiallyIndexedInSolr(UpgradeStep):
    """Fix docs only partially indexed in solr.

    We think affected documents may have been not indexed in solr at all due to
    a bug with date serialization in `ftw.solr`. The bug was only fixed in
    https://github.com/4teamwork/ftw.solr/pull/158.

    Subsequent edits of the document by users via plone or reindex operations
    during upgrades would have partially indexed or restored the document in
    solr, but only some of the fields as we use atomic updates.

    We've seen that all affected documents do not have the created date set as
    we never manually reindex it, as it never changes. Thus apply a heuristic
    to detect broken solr documents. We assume that broken documents do not
    have the field 'created' set to a value in solr.
    """

    deferrable = True

    @property
    def is_solr_enabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISolrSettings)
        return settings.enabled

    def __call__(self):
        if not self.is_solr_enabled:
            return

        self.solr_connection = getUtility(ISolrConnectionManager).connection
        broken_docs = self.find_broken_solr_docs()
        for doc in broken_docs:
            self.reindex_broken_doc(doc)

    def find_broken_solr_docs(self):
        """This method purposefully bypasses ISolrSearch.

        We have to build our own query as ISolrSearch would insert security
        filters for 'allowedRolesAndUsers'. But there are broken solr docs
        where the 'allowedRolesAndUsers' is missing.
        """
        params = {
            u'offset': 0,
            # this queries for all docs where the `created` field is not set
            u'query': u'-created:[* TO *]',
            # choose a very high number well beyond the number of docs we can
            # possibly have, but also well below java max 4 byte int 2147483647
            u'limit': 99999999,
            # only return the UID field
            u'params': {
                u'fl': u'UID'
            }
        }

        solr_response = self.solr_connection.search(
            params, request_handler=u'/select')
        return solr_response.docs

    def reindex_broken_doc(self, doc):
        """Reindex all fields/indexes for a broken solr document.
        """
        plone_uid = doc[u'UID']
        brains = self.catalog_unrestricted_search({u'UID': plone_uid})
        if len(brains) != 1:
            logger.error(
                u'Could not find a unique brain for the UID={}'.format(
                    plone_uid)
            )
            return

        brain = brains[0]
        obj = self.catalog_unrestricted_get_object(brain)
        # `catalog_unrestricted_get_object` takes care of logging already
        if obj:
            # we reindex the whole object as we cannot know which fields are
            # missing, also do catalog reindex for convenience
            obj.reindexObject()
