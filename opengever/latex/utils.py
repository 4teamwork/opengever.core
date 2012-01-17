from Products.CMFCore.utils import getToolByName
from opengever.globalindex.interfaces import ITaskQuery
from zope.component import getUtility


def get_selected_items(context, request):
    """Returns either a set of brains or a set of SQLAlchemy objects -
    depending on the (tabbed-) view where the tasks were selected.
    If there is a "path:list" in the request, we use the catalog and
    if there is a "task_id:list", we use SQLAlchemy.
    """

    paths = request.get('paths', None)
    ids = request.get('task_ids', [])

    if paths:
        catalog = getToolByName(context, 'portal_catalog')

        for path in request.get('paths', []):
            brains = catalog({'path': {'query': path,
                                   'depth': 0}})
            assert len(brains) == 1, "Could not find task at %s" % path
            yield brains[0]

    elif ids:
        query = getUtility(ITaskQuery)

        # we need to sort the result by our ids list, because the
        # sql query result is not sorted...
        # create a mapping:
        mapping = {}
        for task in query.get_tasks(ids):
            mapping[str(task.task_id)] = task

        # get the task from the mapping
        for taskid in ids:
            task = mapping.get(str(taskid))
            if task:
                yield task

    else:
        # empty generator
        pass
