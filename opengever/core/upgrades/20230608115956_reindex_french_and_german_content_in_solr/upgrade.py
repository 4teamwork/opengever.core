from ftw.solr.interfaces import ISolrSearch
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from zope.component import getUtility


class ReindexFrenchAndGermanContentInSolr(UpgradeStep):
    """Reindex french and german content in solr.
    """

    deferrable = True

    def __call__(self):
        self.reindex()

    def reindex(self):
        solr = getUtility(ISolrSearch)
        fq = [
            "SearchableText_fr:['' TO *] "
            "OR title_fr:['' TO *] "
            "OR Description_fr:['' TO *] "
            "OR Title_fr:['' TO *] "
            "OR SearchableText_en:['' TO *] "
            "OR title_en:['' TO *] "
            "OR Description_en:['' TO *] "
            "OR Title_en:['' TO *]"
        ]

        fl = ['UID']
        nrows = solr.search(fq=fq, rows=0).num_found
        resp = solr.search(fq=fq, fl=fl, rows=nrows)

        with NightlyIndexer(idxs=[], index_in_solr_only=True) as indexer:
            for doc in ProgressLogger('Reindex french or english content', resp.docs):
                indexer.add_by_solr_document(doc)
