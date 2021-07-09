from ftw.upgrade import UpgradeStep
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema


class IndexSequenceTypeInSolr(UpgradeStep):
    """Index sequence_type in solr.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': ITaskTemplateFolderSchema.__identifier__}
        for folder in self.objects(query, 'Reindex tasktemplatefolder sequence_type'):
            folder.reindexObject(idxs=['UID', 'sequence_type'])
