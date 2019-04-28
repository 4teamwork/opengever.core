from ftw.upgrade import UpgradeStep


class AddBooleanIndexAfterResolveJobsPending(UpgradeStep):
    """Add BooleanIndex after_resolve_jobs_pending.
    """

    def __call__(self):
        self.catalog_add_index('after_resolve_jobs_pending', 'BooleanIndex')
        # No reindexing required
