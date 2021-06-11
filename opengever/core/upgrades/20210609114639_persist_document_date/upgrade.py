from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata


class PersistDocumentDate(UpgradeStep):
    """Persist document date.
    """
    deferrable = True

    def is_document_date_persisted(self, obj):
        if obj._p_changed is None:
            # Object is a ghost, we need to make sure it gets loaded by
            # accessing any attribute. Accessing __dict__ does not trigger
            # loading of the object.
            obj.created()
        return "document_date" in obj.__dict__

    def __call__(self):
        query = {'object_provides': IDocumentMetadata.__identifier__}
        for obj in self.objects(query, "Persist document_date on documents"):
            if self.is_document_date_persisted(obj):
                continue

            IDocumentMetadata(obj).document_date = obj.created().asdatetime().date()
            obj.reindexObject(idxs=["document_date"])
