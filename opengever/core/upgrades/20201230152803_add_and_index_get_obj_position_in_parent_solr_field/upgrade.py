from ftw.upgrade import UpgradeStep
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IToDoList


class AddAndIndexGetObjPositionInParentSolrField(UpgradeStep):
    """Add and index get obj position in parent solr field.
    """
    deferrable = True

    def __call__(self):
        query = {'object_provides': [
            ITaskTemplate.__identifier__,
            IToDo.__identifier__,
            IToDoList.__identifier__
        ]}

        for obj in self.objects(query, 'Index getObjPositionInParent field in solr.'):
            obj.reindexObject(idxs=['getObjPositionInParent'])
