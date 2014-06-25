from ftw.upgrade import UpgradeStep


class MigrateSubdossierColumnData(UpgradeStep):

    def __call__(self):
        """This method is implemented in each upgrade step with the
        tasks the upgrade should perform.
        """
        self.index_new_task_columns()

    def index_new_task_columns(self):
        for task in self.objects({'portal_type': 'opengever.task.task'},
                                  'Get tasks'):
            sqltask = task.get_sql_object()
            sqltask.containing_subdossier = task.get_containing_subdossier()
            sqltask.text = task.text
