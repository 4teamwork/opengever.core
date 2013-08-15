from ftw.upgrade import UpgradeStep


class UpdateTaskWorkflow(UpgradeStep):

    def __call__(self):
        self.update_workflow()

        for obj in self.objects(
                {'object_provides': 'opengever.task.task.ITask'},
                'Update tasks security'):
            self.update_security(obj, reindex_security=False)

    def update_workflow(self):
        self.portal_setup.runImportStepFromProfile(
            'profile-opengever.task.upgrades:2601', 'workflow')
