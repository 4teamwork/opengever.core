from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from Products.CMFPlone.utils import safe_unicode


class EnableFtwKeywordwidgetForDocumentMetadataBehavior(UpgradeStep):
    """Enable ftw keywordwidget for document metadata behavior.
    """

    query = {'object_provides': [IDocumentMetadata.__identifier__]}

    def __call__(self):
        self.install_upgrade_profile()
        self.ensure_utf_8_keywords()
        self.catalog_reindex_objects(self.query, idxs=['Subject', ])

    def ensure_utf_8_keywords(self):
        for obj in self.objects(self.query, 'Ensure keywords are utf-8'):
            doc = IDocumentMetadata(obj)
            doc.keywords = tuple(
                safe_unicode(keyword).encode('utf-8')
                for keyword in doc.keywords)
