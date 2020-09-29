from ftw.upgrade import UpgradeStep
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from zope.annotation.interfaces import IAnnotations


iold = 'opengever.dossier.behaviors.dossier.IDossier'
inew = 'opengever.dossier.dossiertemplate.behaviors.IDossierTemplate'

TO_MIGRATE = (
    ('{}.keywords'.format(iold), '{}.keywords'.format(inew)),
    ('{}.comments'.format(iold), '{}.comments'.format(inew)),
    ('{}.filing_prefix'.format(iold), '{}.filing_prefix'.format(inew))
)

TO_DELETE = (
    '{}.keywords'.format(iold),
    '{}.start'.format(iold),
    '{}.end'.format(iold),
    '{}.touched'.format(iold),
    '{}.comments'.format(iold),
    '{}.responsible'.format(iold),
    '{}.external_reference'.format(iold),
    '{}.filing_prefix'.format(iold),
    '{}.temporary_former_reference_number'.format(iold),
    '{}.container_type'.format(iold),
    '{}.number_of_containers'.format(iold),
    '{}.container_location'.format(iold),
    '{}.relatedDossier'.format(iold),
    '{}.former_reference_number'.format(iold),
    '{}.reference_number'.format(iold)
    )


class MigrateIDossierTemplateFieldsStorage(UpgradeStep):
    """Migrate IDossierTemplate fields storage from IDossier
    to IDossierTemplate.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': IDossierTemplateMarker.__identifier__}
        for obj in self.objects(query, 'Migrate IDossierTemplate fields storage'):
            annotations = IAnnotations(obj)
            for old_field, new_field in TO_MIGRATE:
                if old_field in annotations:
                    annotations[new_field] = annotations[old_field]
            for field in TO_DELETE:
                if field in annotations:
                    annotations.pop(field)
