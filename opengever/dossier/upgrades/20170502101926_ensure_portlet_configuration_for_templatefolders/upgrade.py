from ftw.upgrade import UpgradeStep
from opengever.dossier.templatefolder.subscribers import configure_templatefolder_portlets


class EnsurePortletConfigurationForTemplatefolders(UpgradeStep):
    """Ensure portlet configuration for templatefolders.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.dossier.templatefolder']},
                u'Ensure portlet configuration for templatefolders'):

            configure_templatefolder_portlets(obj, event=None)
