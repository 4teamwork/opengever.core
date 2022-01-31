from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import DossierCommentsMigrator
from opengever.dossier.behaviors.dossier import IDossierMarker


class MigrateDossierComments(UpgradeStep):
    """Migrate dossier comments.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': IDossierMarker.__identifier__}
        with DossierCommentsMigrator() as comment_migrator:
            for brain in self.brains(query, 'Migtate dossier comments'):
                comment_migrator.add_by_brain(brain)
