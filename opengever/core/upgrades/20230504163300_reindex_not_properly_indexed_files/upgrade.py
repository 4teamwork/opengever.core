from ftw.solr.interfaces import ISolrSearch
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.base.solr import OGSolrDocument
from opengever.core.upgrade import NightlyIndexer
from zope.component import getUtility


class ReindexNotProperlyIndexedFiles(UpgradeStep):
    """Reindex not properly indexed files.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        self.reindex()

    def reindex(self):
        solr = getUtility(ISolrSearch)
        fq = [
            "portal_type:(opengever.document.document OR ftw.mail.mail)",
            "-filename:['' TO *]"]
        fl = ['filename', 'path']

        nrows = solr.search(fq=fq, rows=0).num_found
        resp = solr.search(fq=fq, fl=fl, rows=nrows)

        with NightlyIndexer(idxs=[], index_in_solr_only=True) as indexer:
            for doc in ProgressLogger('Maybe reindex not properly indexed files', resp.docs):
                obj = OGSolrDocument(doc).getObject()

                # We still need to check if the filename is really empty becuase the
                # query will return docs with a filename beginning with an empty string.:
                # Example: {u'filename': u' my-filename.docx'}
                if not doc.get('filename') and obj.get_filename():
                    indexer.add_by_obj(obj)
