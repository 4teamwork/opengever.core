from ftw.upgrade import UpgradeStep
from plone import api
from zope.annotation.interfaces import IAnnotations


ANNOTATIONS_DATA_KEY = 'opengever.workspace : invitations'


class RemoveOldWorkspaceInvitations(UpgradeStep):
    """Remove old workspace invitations.
    """

    def __call__(self):
        annotations = IAnnotations(api.portal.get())

        if ANNOTATIONS_DATA_KEY in annotations:
            del annotations[ANNOTATIONS_DATA_KEY]
