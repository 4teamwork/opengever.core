from ftw.upgrade import UpgradeStep
from opengever.base.portlets import add_navigation_portlet_assignment
from opengever.base.portlets import block_context_portlet_inheritance
from plone import api


class EnsurePortletConfigurationForInboxesAndInboxcontainers(UpgradeStep):
    """Ensure portlet configuration for inboxes and inboxcontainers.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.inbox.container']},
                u'Ensure portlet configuration for inboxcontainers'):

            block_context_portlet_inheritance(obj)

        for obj in self.objects(
                {'portal_type': ['opengever.inbox.inbox']},
                u'Ensure portlet configuration for inboxes'):

            block_context_portlet_inheritance(obj)

            url_tool = api.portal.get_tool('portal_url')
            add_navigation_portlet_assignment(
                obj,
                root=u'/'.join(url_tool.getRelativeContentPath(obj)),
                topLevel=0)
