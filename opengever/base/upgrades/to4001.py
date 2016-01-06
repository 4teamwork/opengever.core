from ftw.upgrade import UpgradeStep


class AddModifiedSecondsIndex(UpgradeStep):

    def __call__(self):
        # The modified_seconds index is no longer required,
        # so there is no need to add it.
        # The upgrade step 4606@opengever.base:default will
        # remove the index when it exists.
        # See https://github.com/4teamwork/opengever.core/pull/1504
        return
