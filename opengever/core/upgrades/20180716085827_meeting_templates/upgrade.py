from ftw.upgrade import UpgradeStep


class MeetingTemplates(UpgradeStep):
    """Meeting Templates.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_templatefolder_workflow'],
                                      reindex_security=False)
