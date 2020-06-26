from ftw.upgrade import UpgradeStep


class IndexTaskTemplateDeadlineAsPeriod(UpgradeStep):
    """Index task template deadline as period (Solr only).
    """
    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        # `period` is not an index in the catalog, only a field in Solr. In order
        # avoid reindexing the whole objects, we must pick any index that exists
        # for all objects and is fast to compute, `UID` in this case.
        self.catalog_reindex_objects(
            {"portal_type": "opengever.tasktemplates.tasktemplate"},
            idxs=["UID", "period"]
        )
