from ftw.upgrade import UpgradeStep


class AddOneoffixxTemplateFilterTagSetting(UpgradeStep):
    """Add oneoffixx template_filter_tag setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
