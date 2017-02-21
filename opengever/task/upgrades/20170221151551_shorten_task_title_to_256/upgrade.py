from ftw.upgrade import UpgradeStep


class ShortenTaskTitleTo256(UpgradeStep):
    """Shorten task title to 256.
    """

    def __call__(self):
        query = {'portal_type': 'opengever.task.task'}
        for task in self.objects(query, "Shorten task titles"):
            title = task.safe_title
            if len(title) > 256:
                task.title = title[:256]
                task.reindexObject(idxs=['Title', 'SearchableText'])

        self.install_upgrade_profile()
