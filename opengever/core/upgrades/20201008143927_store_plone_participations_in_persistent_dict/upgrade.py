from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations


class StorePloneParticipationsInPersistentDict(UpgradeStep):
    """Store plone participations in persistent dict.
    """
    deferrable = True
    annotation_key = 'participations'

    def __call__(self):
        """We migrate all plone participations from PersistentList to
        PersistenDict. We do not restrict the upgrade step to deployments
        with the contact feature disabled, as it seems we did not migrate
        the data when we switched STABS to the new contact implementation
        and I don't want to leave unmigrated data behind
        """
        query = {'object_provides': IParticipationAwareMarker.__identifier__}
        for dossier in self.objects(query, 'Merge participations.'):
            annotations = IAnnotations(dossier)
            if self.annotation_key not in annotations:
                continue

            participation_list = annotations.pop(self.annotation_key)
            if not participation_list:
                # No need to store an empty dictionnary
                continue

            participation_dict = PersistentDict()
            for participation in participation_list:
                participation_dict[participation.contact] = participation
            annotations[self.annotation_key] = participation_dict
