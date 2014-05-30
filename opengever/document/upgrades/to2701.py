from ftw.upgrade import UpgradeStep
from zope.annotation import IAnnotations
from z3c.relationfield.interfaces import IHasRelations


OLD_KEY = 'opengever.document.behaviors.IRelatedDocuments.relatedItems'
NEW_KEY = 'opengever.document.behaviors.related_docs.IRelatedDocuments.relatedItems'


class RenameDocumentBehaviors(UpgradeStep):
    """Rename behavior dotted names in og.document.document FTI and
    migrate relatedItems annotations.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.document.upgrades:2701')
        self._migrate_related_items_annotations()

    def _migrate_related_items_annotations(self):
        query = {'portal_type': 'opengever.document.document',
                 'object_provides': IHasRelations.__identifier__}
        for obj in self.objects(query, 'Migrate relatedItems annotations'):
            ann = IAnnotations(obj)
            if not NEW_KEY in ann and OLD_KEY in ann:
                ann[NEW_KEY] = ann[OLD_KEY]
                ann.pop(OLD_KEY)