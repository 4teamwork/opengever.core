from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema


class IndexIsSubtasktemplatefolder(UpgradeStep):
    """Index is_subtasktemplatefolder.
    """

    deferrable = True

    def __call__(self):
        query = {
            "object_provides": ITaskTemplateFolderSchema.__identifier__,
        }

        with NightlyIndexer(
            idxs=["is_subtasktemplatefolder"],
            index_in_solr_only=True,
        ) as indexer:
            for brain in self.brains(query, "Index is_subtasktemplatefolder field in Solr"):
                indexer.add_by_brain(brain)
