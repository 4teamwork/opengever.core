from opengever.api.dossier_participations import available_roles
from opengever.api.dossier_participations import primary_participation_roles
from plone.restapi.services import Service


class SystemInformationGet(Service):
    """GEVER system information"""

    def reply(self):
        infos = {}
        self.add_dossier_participation_roles(infos)
        return infos

    def add_dossier_participation_roles(self, infos):
        available_participation_roles = available_roles(self.context)
        primary_participation_role_ids = {
            role.get('token') for role
            in primary_participation_roles(self.context)}
        for role in available_participation_roles:
            role['primary'] = role.get('token') in primary_participation_role_ids
        infos['dossier_participation_roles'] = available_participation_roles
