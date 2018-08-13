from ftw.upgrade import UpgradeStep


class ExcludePreconditionFailedFromErrorLog(UpgradeStep):
    """Exclude precondition failed from error log.
    """

    def __call__(self):
        self.configure_error_log()

    def configure_error_log(self):
        error_log = self.getToolByName('error_log')
        properties = error_log.getProperties()
        if 'PreconditionFailed' in properties.get('ignored_exceptions', ()):
            return

        ignored = tuple(properties['ignored_exceptions'])
        ignored += ('PreconditionFailed',)
        properties['ignored_exceptions'] = ignored
        error_log.setProperties(**properties)
