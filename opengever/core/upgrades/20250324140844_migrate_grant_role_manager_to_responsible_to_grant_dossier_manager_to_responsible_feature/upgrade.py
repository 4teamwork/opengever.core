from ftw.upgrade import UpgradeStep
from opengever.base.role_assignments import ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossierMarker
from opengever.dossier.interfaces import IDossierSettings
from plone import api
import logging


log = logging.getLogger('ftw.upgrade')


class MigrateGrantRoleManagerToResponsibleToGrantDossierManagerToResponsibleFeature(UpgradeStep):
    """Migrate grant role manager to responsible to grant dossier manager to responsible feature.
    """

    def __call__(self):
        self.migrate_feature()

        # important: run upgrade profile after the migration. It removes the
        # registry entry which is required to successfully migrate the settings.
        self.install_upgrade_profile()

    def migrate_feature(self):
        registry = api.portal.get_tool('portal_registry')

        # The interface field may no longer exist when executing this upgradestep.
        # Thus, we need to use the fully dotted registry key to be able to retrieve
        # the old registry value.
        is_grant_role_manager_to_responsible_enabled = registry.get(
            'opengever.dossier.interfaces.IDossierSettings.grant_role_manager_to_responsible')

        if not is_grant_role_manager_to_responsible_enabled:
            log.info('Feature grant_role_manager_to_responsible was not in use. '
                     'There is no need to migrate anything')
            return

        api.portal.set_registry_record('grant_dossier_manager_to_responsible',
                                       True, IDossierSettings)

        query = {'object_provides': IProtectDossierMarker.__identifier__}
        msg = "Grant dossier manager to responsible and remove role manager role"

        for obj in self.objects(query, msg):
            # Clear old role assignment which assigned the "Role manager" role
            manager = RoleAssignmentManager(obj)
            manager.clear_by_causes([ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE])

            # Get the current responsible. Even if the responsible is required
            # on a dossier, it's possible to have dossiers without any responsible
            # or dossiers with a non existing responsible.
            # Both should not happen, but is possible. We skip such dossiers.
            responsible = IDossier(obj).responsible
            if not responsible or not api.user.get(responsible):
                continue

            # Assign the new assignment dossier manager roles.
            dossier_protection = IProtectDossier(obj)
            dossier_protection.dossier_manager = responsible

            # Check if the user already have had view permission on the object.
            # We use this information later on to decide if we need to reindex
            # the object security of the object.
            need_reindex = not api.user.has_permission(
                'View', dossier_protection.dossier_manager, obj=obj)

            # Grant the dossier manager role to the dossier responsible
            dossier_protection.grant_dossier_manager_roles()

            if need_reindex:
                obj.reindexObjectSecurity()
