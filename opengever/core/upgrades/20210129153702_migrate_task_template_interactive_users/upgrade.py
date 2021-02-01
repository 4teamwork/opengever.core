from ftw.upgrade import UpgradeStep
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate


class MigrateTaskTemplateInteractiveUsers(UpgradeStep):
    """Migrate task template interactive users.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': [
            ITaskTemplate.__identifier__,
        ]}

        for obj in self.objects(query, 'Migrate tasktemplate interactive users'):
            if obj.issuer in ['responsible', 'current_user']:
                obj.issuer = 'interactive_actor:{}'.format(obj.issuer)
                obj.reindexObject(idxs=['issuer'])

            if obj.responsible_client == 'interactive_users':
                obj.responsible_client = None
                obj.responsible = 'interactive_actor:{}'.format(obj.responsible)
                obj.reindexObject(idxs=['responsible'])
