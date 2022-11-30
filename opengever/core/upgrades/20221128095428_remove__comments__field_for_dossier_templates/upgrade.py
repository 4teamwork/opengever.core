from ftw.upgrade import UpgradeStep
from zope.annotation import IAnnotations


KEY_TO_REMOVE = 'opengever.dossier.dossiertemplate.behaviors.IDossierTemplate.comments'  # noqa
IFACE = 'opengever.dossier.dossiertemplate.behaviors.IDossierTemplateMarker'


class Remove_comments_fieldForDossierTemplates(UpgradeStep):
    """Remove 'comments' field for dossier templates.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': [IFACE]}

        msg = "Delete 'comments' field for existing dossier templates"
        for obj in self.objects(query, msg):
            ann = IAnnotations(obj)
            ann.pop(KEY_TO_REMOVE, None)
