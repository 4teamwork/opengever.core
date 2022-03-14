from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.core.upgrade import NightlyIndexer


class AddTranslatedTitleFieldsToSolr(UpgradeStep):
    """Add translated title fields to Solr."""

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        query = {
            "object_provides": ITranslatedTitleSupport.__identifier__,
        }

        with NightlyIndexer(
            idxs=["title_de", "title_en", "title_fr"],
            index_in_solr_only=True,
        ) as indexer:
            for brain in self.brains(query, "Index translated title fields in Solr"):
                indexer.add_by_brain(brain)
