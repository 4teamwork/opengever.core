from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.changed import IChanged
from opengever.base.behaviors.touched import ITouched
from opengever.dossier.behaviors.dossier import IDossier


class AddITouchedBehavior(UpgradeStep):
    """Add i touched behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.migrate_touched_to_new_behavior()
        self.index_changed_on_todos_and_todo_lists()
        self.index_touched_on_worskspaces()

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

    def index_touched_on_worskspaces(self):
        query = {'object_provides': 'opengever.workspace.interfaces.IWorkspace'}
        for obj in self.objects(query, "Index touched on workspaces."):
            # Get the last changed object within the workspace or the workspace
            # itself to determine the current touched date.
            ITouched(obj).touched = self.catalog_unrestricted_search(
                {
                    'path': {'query': '/'.join(obj.getPhysicalPath())},
                    'sort_on': 'changed',
                    'sort_order': 'descending',
                    'sort_limit': 1
                }
            )[0].changed

            obj.reindexObject(idxs=['UID', 'touched'])

    def index_changed_on_todos_and_todo_lists(self):
        query = {'object_provides': ['opengever.workspace.interfaces.IToDo',
                                     'opengever.workspace.interfaces.IToDoList']}
        for obj in self.objects(query, "Index changed on todos and todolists."):
            IChanged(obj).changed = obj.modified()
            obj.reindexObject(idxs=['UID', 'changed'])
