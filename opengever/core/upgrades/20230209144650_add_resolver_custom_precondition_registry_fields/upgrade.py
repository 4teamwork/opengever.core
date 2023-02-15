from ftw.upgrade import UpgradeStep


class AddResolverCustomPreconditionRegistryFields(UpgradeStep):
    """Add resolver_custom_precondition and
    resolver_custom_precondition_error_text_de registry fields.
    """

    def __call__(self):
        self.install_upgrade_profile()
