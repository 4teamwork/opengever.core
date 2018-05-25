from ftw.upgrade import UpgradeStep
from opengever.tasktemplates.tasktemplatefolder import TaskTemplateFolder


class AddSeperateClassForTasktemplates(UpgradeStep):
    """add seperate class for tasktemplates.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'portal_type': 'opengever.tasktemplates.tasktemplatefolder'}
        msg = 'Migrate tasktemplatefolder class'

        for tasktemplatefolder in self.objects(query, msg):
            self.migrate_class(tasktemplatefolder, TaskTemplateFolder)
