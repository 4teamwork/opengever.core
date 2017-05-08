from ftw.upgrade import UpgradeStep
from opengever.meeting.handlers import configure_committee_container_portlets


class EnsurePortletConfigurationForCommitteecontainers(UpgradeStep):
    """Ensure portlet configuration for committeecontainers.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.meeting.committeecontainer']},
                u'Ensure portlet configuration for committeecontainers'):

            configure_committee_container_portlets(obj, event=None)
