from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep


class UpdateWorkflow(UpgradeStep):

    def __call__(self):
        self.update_workflow()

        objects = self.catalog_unrestricted_search(
            {'object_provides': 'opengever.task.task.ITask'},
            full_objects=True)

        with ProgressLogger('Update tasks security', objects) as step:
            for obj in objects:
                self.update_security(obj, reindex_security=False)
                step()

    def update_workflow(self):
        self.portal_setup.runImportStepFromProfile(
            'profile-opengever.task:default',
            'workflow')
