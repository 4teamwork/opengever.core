"""
Helpers for migrating user-related data on dossiers.
"""

from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.ogds.base.utils import ogds_service
from opengever.usermigration.exceptions import UserMigrationException
from plone import api
import logging


logger = logging.getLogger('opengever.usermigration')


class DossierMigrator(object):

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "DossierMigrator only supports 'move' mode as of yet")
        self.mode = mode

        self.strict = strict
        self.catalog = api.portal.get_tool('portal_catalog')

    def _get_dossiers(self):
        dossier_brains = self.catalog.unrestrictedSearchResults(
            object_provides=IDossierMarker.__identifier__)

        for brain in dossier_brains:
            yield brain.getObject()

    def _verify_user(self, userid):
        ogds_user = ogds_service().fetch_user(userid)
        if ogds_user is None:
            msg = "User '{}' not found in OGDS!".format(userid)
            if self.strict:
                raise UserMigrationException(msg)
            else:
                logger.warn(msg)

    def _migrate_responsible(self, dossier):
        moved = []
        modified_idxs = []
        path = '/'.join(dossier.getPhysicalPath())

        old_userid = IDossier(dossier).responsible

        if old_userid in self.principal_mapping:
            new_userid = self.principal_mapping[old_userid]
            logger.info("Migrating responsible for {} ({} -> {})".format(
                path, old_userid, new_userid))
            self._verify_user(new_userid)
            IDossier(dossier).responsible = new_userid

            moved.append((path, old_userid, new_userid))
            modified_idxs = ['responsible']

        return modified_idxs, moved

    def _migrate_participations(self, dossier):
        moved = []
        modified_idxs = []
        path = '/'.join(dossier.getPhysicalPath())

        if not IParticipationAwareMarker.providedBy(dossier):
            # No participation support - probably a template dossier
            return modified_idxs, moved

        phandler = IParticipationAware(dossier)
        participations = phandler.get_participations()
        for participation in participations:
            old_userid = participation.contact
            if old_userid in self.principal_mapping:
                new_userid = self.principal_mapping[old_userid]
                logger.info("Migrating participation for {} ({} -> {})".format(
                    path, old_userid, new_userid))
                self._verify_user(new_userid)
                participation.contact = new_userid
                moved.append((path, old_userid, new_userid))

        return modified_idxs, moved

    def migrate(self):
        responsibles_moved = []
        participations_moved = []

        dossiers = self._get_dossiers()

        for dossier in dossiers:
            modified_idxs = []

            # Migrate responsible
            idxs, moved = self._migrate_responsible(dossier)
            modified_idxs.extend(idxs)
            responsibles_moved.extend(moved)

            # Migrate participations
            idxs, moved = self._migrate_participations(dossier)
            modified_idxs.extend(idxs)
            participations_moved.extend(moved)

            dossier.reindexObject(idxs=modified_idxs)

        results = {
            'responsibles': {
                'moved': responsibles_moved, 'copied': [], 'deleted': []},
            'participations': {
                'moved': participations_moved, 'copied': [], 'deleted': []},
        }

        return results
