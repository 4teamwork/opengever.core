from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility


class ResolveDocumentAuthor(UpgradeStep):
    """Resolve document_author for all documents"""

    def __call__(self):
        self.info = getUtility(IContactInformation)
        self.user_ids = [user.userid for user in self.info.list_users()]

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
            document.document_author = self.info.describe(
                document_author,
                with_principal=False,
                with_email=False)

            document.reindexObject(idxs=['sortable_author'])
