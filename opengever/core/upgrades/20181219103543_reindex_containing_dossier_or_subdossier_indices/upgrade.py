from ftw.upgrade import UpgradeStep
from opengever.dossier.interfaces import IDossierMarker


TYPES_WITH_CONTAINING_DOSSIER_INDEX = ('opengever.dossier.businesscasedossier',
                                       'opengever.meeting.proposal',
                                       'opengever.workspace.folder',
                                       'opengever.document.document',
                                       'opengever.task.task',
                                       'opengever.private.dossier',
                                       'ftw.mail.mail',
                                       'opengever.meeting.meetingdossier',
                                       'opengever.workspace.workspace')

TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX = ('opengever.document.document',
                                          'opengever.task.task',
                                          'ftw.mail.mail')


class ReindexContainingDossierOrSubdossierIndices(UpgradeStep):
    """Reindex containing_dossier, containing_subdossier and
    is_subdossier indices.
    """

    deferrable = True

    def __call__(self):
        message = "Ensure containing_dossier, containing_subdossier and "
        message += "is_subdossier are properly indexed on all objects"

        for obj in self.objects({'portal_type': TYPES_WITH_CONTAINING_DOSSIER_INDEX}, message):
            if IDossierMarker.providedBy(obj):
                obj.reindexObject(idxs=["is_subdossier", "containing_dossier"])

            elif obj.portal_type in TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX:
                obj.reindexObject(idxs=["is_subdossier", "containing_dossier",
                                        "containing_subdossier"])
            else:
                obj.reindexObject(idxs=["containing_dossier"])
