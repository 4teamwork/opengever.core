from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask
from opengever.tasktemplates.interfaces import IContainParallelProcess
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.tasktemplates.interfaces import IPartOfParallelProcess
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class MigrateTaskProcessMakerInterfaces(UpgradeStep):
    """Migrate task process maker interfaces.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # sequential
        self.migrate_marker_interfaces(IFromSequentialTasktemplate,
                                       IContainSequentialProcess,
                                       IPartOfSequentialProcess)

        # parallel
        self.migrate_marker_interfaces(IFromParallelTasktemplate,
                                       IContainParallelProcess,
                                       IPartOfParallelProcess)

    def migrate_marker_interfaces(self, old_marker, new_marker, sub_marker):
        query = {'object_provides': old_marker.__identifier__,
                 'is_subtask': False}
        msg = 'Migrate {} interface'.format(old_marker)

        for task in self.objects(query, msg):
            self.replace_marker(task, new_marker, old_marker)

            # Because in old implementation adding a task to a process,
            # has not resulted in the new task provides the marker
            # interfaces. Therefore we need to update all subtasks
            for subtask in task.objectValues():
                if ITask.providedBy(subtask):
                    self.replace_marker(subtask, sub_marker, old_marker)

    def replace_marker(self, task, new_iface, old_iface):
        alsoProvides(task, new_iface)
        noLongerProvides(task, old_iface)
        task.reindexObject(idxs=['object_provides'])
