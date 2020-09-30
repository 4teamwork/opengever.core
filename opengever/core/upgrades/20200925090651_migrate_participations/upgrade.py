from ftw.upgrade import UpgradeStep
from opengever.contact import is_contact_feature_enabled
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from persistent.list import PersistentList


class MigrateParticipations(UpgradeStep):
    """Migrate participations.
    """
    deferrable = True

    def __call__(self):
        if is_contact_feature_enabled():
            return
        query = {'object_provides': IParticipationAwareMarker.__identifier__}
        for dossier in self.objects(query, 'Merge participations.'):
            handler = IParticipationAware(dossier)
            old_participations = handler.get_participations()
            if not old_participations:
                continue
            contacts_and_roles = dict()
            for participation in old_participations:
                if participation.contact in contacts_and_roles:
                    contacts_and_roles[participation.contact].update(participation.roles)
                else:
                    contacts_and_roles[participation.contact] = set(participation.roles)

            lst = PersistentList([handler.create_participation(contact=key, roles=value)
                                  for key, value in contacts_and_roles.items()])
            handler.set_participations(lst)
