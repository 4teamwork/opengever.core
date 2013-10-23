from ftw.upgrade import UpgradeStep
from opengever.base.adapters import CHILD_REF_KEY, PREFIX_REF_KEY
from opengever.base.adapters import REPOSITORY_FOLDER_KEY, DOSSIER_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class CleanupReferencePrefixMapping(UpgradeStep):

    def __call__(self):
        for repository in self.objects(
                {'portal_type': 'opengever.repository.repositoryfolder'},
                'Cleanup reference prefix mapping on repositoryfolders'):
            self.move_repository_reference_mappings(repository)

        for dossier in self.objects(
                {'object_provides':
                 'opengever.dossier.behaviors.dossier.IDossierMarker'},
                'Cleanup reference prefix mapping on dossiers'):
            self.move_dossier_mappings(repository)

    def move_repository_reference_mappings(self, obj):
        intids = getUtility(IIntIds)
        annotations = IAnnotations(obj)

        if annotations and annotations.get(CHILD_REF_KEY):
            repository_mapping = PersistentDict(
                {CHILD_REF_KEY: {},
                 PREFIX_REF_KEY: {}})
            dossier_mapping = PersistentDict(
                {CHILD_REF_KEY: {},
                 PREFIX_REF_KEY: {}})

            for number, intid in annotations.get(CHILD_REF_KEY).items():
                try:
                    child = intids.getObject(intid)
                except KeyError:
                    # the object with this intid does not longer exist.
                    continue

                if IDossierMarker.providedBy(child):
                    dossier_mapping[CHILD_REF_KEY][number] = intid
                    dossier_mapping[PREFIX_REF_KEY][intid] = number
                else:
                    repository_mapping[CHILD_REF_KEY][number] = intid
                    repository_mapping[PREFIX_REF_KEY][intid] = number

            # save mapping
            annotations[REPOSITORY_FOLDER_KEY] = repository_mapping
            annotations[DOSSIER_KEY] = dossier_mapping

            # drop old mapings
            annotations.pop(CHILD_REF_KEY)
            annotations.pop(PREFIX_REF_KEY)

    def move_dossier_mappings(self, obj):
        annotations = IAnnotations(obj)

        if annotations and annotations.get(CHILD_REF_KEY):
            dossier_mapping = PersistentDict(
                {CHILD_REF_KEY: annotations.get(CHILD_REF_KEY),
                 PREFIX_REF_KEY: annotations.get(PREFIX_REF_KEY)})

            annotations[DOSSIER_KEY] = dossier_mapping

            # drop old mapings
            annotations.pop(CHILD_REF_KEY)
            annotations.pop(PREFIX_REF_KEY)
