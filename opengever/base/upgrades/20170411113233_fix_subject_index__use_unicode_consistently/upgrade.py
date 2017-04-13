from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from plone import api
from Products.CMFPlone.utils import safe_unicode


class FixSubjectIndex_useUnicodeConsistently(UpgradeStep):
    """Fix Subject index, use unicode consistently."""

    def __call__(self):
        self.clear_subject_index()
        self.make_document_keywords_unicode()
        self.make_dossier_keywords_unicode()
        self.recalculate_subject_index()

    def clear_subject_index(self):
        catalog = api.portal.get_tool('portal_catalog')
        catalog.clearIndex('Subject')

    def make_document_keywords_unicode(self):
        query = {'object_provides': [IDocumentMetadata.__identifier__]}
        for obj in self.objects(query, 'Ensure document keywords are unicode'):
            doc = IDocumentMetadata(obj)
            doc.keywords = tuple(
                safe_unicode(keyword) for keyword in doc.keywords)

    def make_dossier_keywords_unicode(self):
        query = {'object_provides': [IDossierTemplateMarker.__identifier__,
                                     IDossierMarker.__identifier__, ]}
        for obj in self.objects(query, 'Ensure dossier keywords are unicode'):
            dossier = IDossier(obj)
            dossier.keywords = tuple(
                safe_unicode(keyword) for keyword in dossier.keywords)

    def recalculate_subject_index(self):
        query = {'object_provides': [IDocumentMetadata.__identifier__,
                                     IDossierTemplateMarker.__identifier__,
                                     IDossierMarker.__identifier__, ]}
        self.catalog_reindex_objects(query, idxs=['Subject', ])
