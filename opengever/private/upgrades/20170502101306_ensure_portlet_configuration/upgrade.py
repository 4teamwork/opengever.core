from ftw.upgrade import UpgradeStep
from opengever.private.subscribers import configure_private_root_portlets


class EnsurePortletConfiguration(UpgradeStep):
    """Ensure portlet configuration for private roots.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.private.root']},
                u'Ensure portlet configuration'):

            configure_private_root_portlets(obj, event=None)
