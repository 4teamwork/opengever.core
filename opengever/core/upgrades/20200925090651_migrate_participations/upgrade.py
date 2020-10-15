from ftw.upgrade import UpgradeStep
from opengever.contact import is_contact_feature_enabled
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations


class MigrateParticipations(UpgradeStep):
    """Migrate participations.
    """
    deferrable = True

    annotation_key = 'participations'

    def __call__(self):
        if is_contact_feature_enabled():
            return
        query = {'object_provides': IParticipationAwareMarker.__identifier__}
        for dossier in self.objects(query, 'Merge participations.'):
            handler = IParticipationAware(dossier)

            annotations = IAnnotations(dossier)
            old_participations = annotations.get(self.annotation_key,
                                                 PersistentList())

            if not old_participations:
                continue
            contacts_and_roles = dict()
            for participation in old_participations:
                if participation.contact in contacts_and_roles:
                    contacts_and_roles[participation.contact].update(participation.roles)
                else:
                    contacts_and_roles[participation.contact] = set(participation.roles)

            lst = PersistentList([handler.create_participation(participant_id=key, roles=value)
                                  for key, value in contacts_and_roles.items()])
            annotations[self.annotation_key] = lst
