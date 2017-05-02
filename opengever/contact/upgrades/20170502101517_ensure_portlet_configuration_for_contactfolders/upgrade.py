from ftw.upgrade import UpgradeStep
from opengever.contact.handlers import configure_contactfolder_portlets


class EnsurePortletConfigurationForContactfolders(UpgradeStep):
    """Ensure portlet configuration for contactfolders.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.contact.contactfolder']},
                u'Ensure portlet configuration for contactfolders'):

            configure_contactfolder_portlets(obj, event=None)
