from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.ogds.models.service import ogds_service


class ResolveDocumentAuthor(UpgradeStep):
    """Resolve document_author for all documents"""

    def __call__(self):
        self.user_ids = [user.userid for user in ogds_service().all_users()]

        catalog = self.getToolByName('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='opengever.document.document')
        with ProgressLogger('Resolve document author', brains) as step:
            for brain in brains:
                self.resolve_document_author(brain)
                step()

    def resolve_document_author(self, brain):
        document_author = brain.document_author

        lower_ids = [id.lower() for id in self.user_ids]

        if document_author and document_author.lower() in lower_ids:
            document = brain.getObject()
            author = ogds_service().find_user(document_author)
            document.document_author = author.label()

            document.reindexObject(idxs=['sortable_author'])
