from ftw.upgrade import UpgradeStep
from opengever.base.default_values import object_has_value_for_field
from opengever.task.task import ITask


class PersistIsPrivateAttributeToTasks(UpgradeStep):
    """Persist is private attribute to tasks.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for task in self.objects(
                {'object_provides': 'opengever.task.task.ITask'},
                "Set default value for is_private attribute for tasks"):
            field = ITask['is_private']

            if object_has_value_for_field(task, field):
                # Skip objects if the object property value is not the field
                # default value. This means, the user (or a script) has already
                # set this value
                continue

            field.set(field.interface(task), field.default)
