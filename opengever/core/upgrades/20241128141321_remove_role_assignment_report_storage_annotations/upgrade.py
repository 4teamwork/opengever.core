from ftw.upgrade import UpgradeStep
from zope.annotation import IAnnotations


ANNOTATIONS_KEY = 'opengever.base.role_assignment_reports'


class RemoveRoleAssignmentReportStorageAnnotations(UpgradeStep):
    """Remove role assignment report storage annotations.
    """

    def __call__(self):
        IAnnotations(self.portal).pop(ANNOTATIONS_KEY, None)
