from ftw.upgrade import UpgradeStep
from opengever.inbox.subscribers import configure_inboxcontainer_portlets
from opengever.inbox.subscribers import configure_inbox_portlets

class EnsurePortletConfigurationForInboxesAndInboxcontainers(UpgradeStep):
    """Ensure portlet configuration for inboxes and inboxcontainers.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.inbox.container']},
                u'Ensure portlet configuration for inboxcontainers'):

            configure_inboxcontainer_portlets(obj, event=None)

        for obj in self.objects(
                {'portal_type': ['opengever.inbox.inbox']},
                u'Ensure portlet configuration for inboxes'):

            configure_inbox_portlets(obj, event=None)
