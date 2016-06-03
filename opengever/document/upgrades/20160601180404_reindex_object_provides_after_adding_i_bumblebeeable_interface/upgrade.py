from ftw.upgrade import UpgradeStep
from plone import api


class ReindexObjectProvidesAfterAddingIBumblebeeableInterface(UpgradeStep):
    """Reindex object_provides after adding IBumblebeeable interface.
    """

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        query = {'portal_type': 'opengever.document.document'}
        msg = 'Reindex object_provides for documents.'

        for obj in self.objects(query, msg):
            catalog.reindexObject(obj, idxs=['object_provides'])
