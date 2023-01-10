from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.touched import ITouched
from opengever.dossier.behaviors.dossier import IDossier


class AddITouchedBehavior(UpgradeStep):
    """Add i touched behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.migrate_touched_to_new_behavior()

    def migrate_touched_to_new_behavior(self):
        TOUCHED_ANNOTATIONS_KEY = '{}.touched'.format(IDossier.__identifier__)
        query = {'object_provides': 'opengever.dossier.behaviors.dossier.IDossierMarker'}
        for obj in self.objects(query, "Migrate touched from IDossier to ITouched."):
            dossier_schema = IDossier(obj)
            if TOUCHED_ANNOTATIONS_KEY in dossier_schema.__dict__['annotations']:
                # We do not need to reindex because the field value does not change.
                # Reassigning the value to the new behavior is enough and
                # fast. So there is also no need for a nightly upgrade step.
                ITouched(obj).touched = dossier_schema.__dict__['annotations'].get(TOUCHED_ANNOTATIONS_KEY)
                del dossier_schema.__dict__['annotations'][TOUCHED_ANNOTATIONS_KEY]
