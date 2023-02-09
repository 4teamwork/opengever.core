from ftw.upgrade import UpgradeStep


class AddResolverCustomRuleRegistryFields(UpgradeStep):
    """Add resolver_custom_rule and resolver_custom_rule_error_text_de
    registry fields.
    """

    def __call__(self):
        self.install_upgrade_profile()
