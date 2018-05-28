from ftw.upgrade import UpgradeStep


class MigrateTaskTemplateFolders(UpgradeStep):
    """Migrate task template folders.
    """

    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.tasktemplates.tasktemplatefolder']},
                "Make sure sequence_type is set for all TaskTempalteFolder"):
            if not obj.sequence_type:
                obj.sequence_type = u"parallel"
