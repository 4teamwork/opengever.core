from ftw.upgrade import UpgradeStep


class RegisterAJsControllerForTheNewHandlebarsImplementedSiteConfigViewTemplate(UpgradeStep):
    """Register a js controller for the new handlebars-implemented site config view template."""

    def __call__(self):
        self.install_upgrade_profile()
