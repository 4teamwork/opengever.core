from ftw.upgrade import UpgradeStep


class FixTaskTemplateResponsibles(UpgradeStep):
    """Fix task template responsibles.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'responsible': 'interactive_actor:None'}
        for obj in self.objects(query, 'Fix task template responsible'):
            obj.responsible = None
            obj.reindexObject(idxs=['responsible'])
