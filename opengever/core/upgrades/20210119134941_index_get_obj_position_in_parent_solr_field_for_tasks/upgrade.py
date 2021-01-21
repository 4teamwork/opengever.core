from ftw.upgrade import UpgradeStep
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate


class IndexGetObjPositionInParentSolrFieldForTasks(UpgradeStep):
    """Index getObjPositionInParent solr field for tasks.
    """

    def __call__(self):
        query = {'object_provides': [
            IFromSequentialTasktemplate.__identifier__,
        ]}

        for obj in self.objects(query, 'Index getObjPositionInParent field in solr.'):
            obj.reindexObject(idxs=['getObjPositionInParent'])
