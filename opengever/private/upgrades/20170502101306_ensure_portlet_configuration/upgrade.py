from ftw.upgrade import UpgradeStep
from opengever.base.portlets import block_context_portlet_inheritance


class EnsurePortletConfiguration(UpgradeStep):
    """Ensure portlet configuration for private roots.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.private.root']},
                u'Ensure portlet configuration'):

            block_context_portlet_inheritance(obj)
