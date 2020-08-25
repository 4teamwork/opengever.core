from ftw.upgrade import UpgradeStep
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from Products.CMFPlone.utils import safe_unicode


class FixDescriptionTypeForDossierTemplates(UpgradeStep):
    """Fix description type for dossier templates.
    """

    def __call__(self):
        query = {'object_provides': IDossierTemplateMarker.__identifier__}
        for obj in self.objects(query, 'Fix dossier template description'):
            description = getattr(obj, 'description', u'')
            obj.description = safe_unicode(description)
