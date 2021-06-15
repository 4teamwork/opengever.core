"""
Helpers for migrating user-related data on dossiers.
"""

from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.usermigration.base import BaseUserMigration
from plone import api
import logging


logger = logging.getLogger('opengever.usermigration')


class DossierMigrator(BaseUserMigration):

    def __init__(self, portal, principal_mapping, mode='move'):
        super(DossierMigrator, self).__init__(
            portal, principal_mapping, mode=mode
        )
        self.catalog = api.portal.get_tool('portal_catalog')
        self.dossiers_to_reindex = set()

    def _get_dossiers(self):
        dossier_brains = self.catalog.unrestrictedSearchResults(
            object_provides=IDossierMarker.__identifier__)

        for brain in dossier_brains:
            yield brain.getObject()

    def _migrate_responsible(self, dossier):
        moved = []
        path = '/'.join(dossier.getPhysicalPath())

        old_userid = IDossier(dossier).responsible

        if old_userid in self.principal_mapping:
            new_userid = self.principal_mapping[old_userid]
            logger.info("Migrating responsible for {} ({} -> {})".format(
                path, old_userid, new_userid))
            self._verify_user(new_userid)
            IDossier(dossier).responsible = new_userid
            self.dossiers_to_reindex.add(dossier)

            moved.append((path, old_userid, new_userid))

        return moved

    def _migrate_participations(self, dossier):
        moved = []
        path = '/'.join(dossier.getPhysicalPath())

        if not IParticipationAwareMarker.providedBy(dossier):
            # No participation support - probably a template folder
            return moved

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

        return moved

    def migrate(self):
        responsibles_moved = []
        participations_moved = []

        dossiers = self._get_dossiers()

        for dossier in dossiers:
            # Migrate responsible
            moved = self._migrate_responsible(dossier)
            responsibles_moved.extend(moved)

            # Migrate participations
            moved = self._migrate_participations(dossier)
            participations_moved.extend(moved)

        # Dossiers with updated responsible need reindexing
        # (participations don't affect indexes however)
        for obj in self.dossiers_to_reindex:
            logger.info("Reindexing dossier: %r" % obj)
            obj.reindexObject(idxs=['responsible', 'SearchableText'])

        results = {
            'responsibles': {
                'moved': responsibles_moved, 'copied': [], 'deleted': []},
            'participations': {
                'moved': participations_moved, 'copied': [], 'deleted': []},
        }

        return results
