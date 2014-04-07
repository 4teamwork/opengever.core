from ftw.upgrade import UpgradeStep
from opengever.base.adapters import CHILD_REF_KEY, PREFIX_REF_KEY
from opengever.base.adapters import REPOSITORY_FOLDER_KEY, DOSSIER_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class CleanupReferencePrefixMapping(UpgradeStep):

    def __call__(self):

        for root in self.objects(
                {'portal_type': 'opengever.repository.repositoryroot'},
                'Cleanup reference prefix mapping on repositoryroots'):
            self.move_repository_root_mappings(root)

        for repository in self.objects(
                {'portal_type': 'opengever.repository.repositoryfolder'},
                'Cleanup reference prefix mapping on repositoryfolders'):
            self.move_repository_reference_mappings(repository)

        for dossier in self.objects(
                {'object_provides':
                 'opengever.dossier.behaviors.dossier.IDossierMarker'},
                'Cleanup reference prefix mapping on dossiers'):
            self.move_dossier_mappings(dossier)

    def move_repository_reference_mappings(self, obj):
        intids = getUtility(IIntIds)
        annotations = IAnnotations(obj)

        if annotations and annotations.get(CHILD_REF_KEY):
            repository_mapping = PersistentDict(
                {CHILD_REF_KEY: PersistentDict(),
                 PREFIX_REF_KEY: PersistentDict()})
            dossier_mapping = PersistentDict(
                {CHILD_REF_KEY: PersistentDict(),
                 PREFIX_REF_KEY: PersistentDict()})

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

            # check new annotations
            if not is_persistent(annotations[REPOSITORY_FOLDER_KEY]):
                raise Exception(
                    "The REPOSITORY_FOLDER_KEY mapping is not persistent for %s." %
                    obj.Title())

            if not is_persistent(annotations[DOSSIER_KEY]):
                raise Exception(
                    "The DOSSIER_KEY mapping is not persistent for %s." % obj.Title())

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

            # check new annotations
            if not is_persistent(annotations[DOSSIER_KEY]):
                raise Exception(
                    "The DOSSIER_KEY mapping is not persistent for %s." % obj.Title())

            # drop old mapings
            annotations.pop(CHILD_REF_KEY)
            annotations.pop(PREFIX_REF_KEY)

    def move_repository_root_mappings(self, obj):
        annotations = IAnnotations(obj)

        if annotations and annotations.get(CHILD_REF_KEY):
            repo_mapping = PersistentDict(
                {CHILD_REF_KEY: annotations.get(CHILD_REF_KEY),
                 PREFIX_REF_KEY: annotations.get(PREFIX_REF_KEY)})

            annotations[REPOSITORY_FOLDER_KEY] = repo_mapping

            # check new annotations
            if not is_persistent(annotations[REPOSITORY_FOLDER_KEY]):
                raise Exception(
                    "The REPOSITORY_FOLDER_KEY mapping is not persistent for %s." %
                    obj.Title())

            # drop old mapings
            annotations.pop(CHILD_REF_KEY)
            annotations.pop(PREFIX_REF_KEY)


def instance_of(obj, types):
    """Checks if item is an instance of any of the types.
    """
    return any([isinstance(obj, t) for t in types])


def is_persistent(thing):
    """Recursive function that checks if a structure containing nested lists
    and dicts uses the Persistent types all the way down.
    """
    if not instance_of(thing, [list, dict]):
        # It's neither a subclass of list or dict, so it's fine
        return True

    if not instance_of(thing, [PersistentList, PersistentDict]):
        # It's a subclass of list or dict, but not a persistent one - bad!
        return False

    if isinstance(thing, PersistentList):
        return all([is_persistent(i) for i in thing])

    elif isinstance(thing, PersistentDict):
        return all([is_persistent(v) for v in thing.values()])
