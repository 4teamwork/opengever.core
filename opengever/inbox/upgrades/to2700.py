from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument
from zope.interface import noLongerProvides


class ReindexInboxDocuments(UpgradeStep):
    """Reindexs the `client_id` and metadata for
    all inbox documents (documents inside the inbox or a yearfoler)."""

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')

        inboxes = catalog(portal_type='opengever.inbox.inbox')
        if not inboxes:
            return
        inbox = inboxes[0]

        query = {'object_provides': IBaseDocument.__identifier__,
                 'path':inbox.getPath()}

        msg = 'Reindex `client_id` for inbox documents'
        for obj in self.objects(query, msg):
            catalog.reindexObject(obj, idxs=['client_id'])
