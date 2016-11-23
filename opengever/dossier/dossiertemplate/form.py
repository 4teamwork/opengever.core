from Products.Five import BrowserView
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled


class SelectTemplateDossierView(BrowserView):
    """ NOT IMPLEMENTED YET
    """

    def is_available(self):
        """Checks if it is allowed to add a 'dossier from template'
        at the current context.
        """
        return is_dossier_template_feature_enabled() and \
            self.context.is_leaf_node()
