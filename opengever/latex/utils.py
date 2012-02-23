from Products.CMFCore.utils import getToolByName
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
import types


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


def get_issuer_of_task(task, with_client=True, with_principal=False):
    info = getUtility(IContactInformation)

    issuer = info.describe(task.issuer, with_principal=with_principal)

    if not with_client:
        return issuer

    if task.predecessor and isinstance(task.predecessor, types.StringTypes):
        # task is a brain or a task object -> predecessor is the oguid
        issuer_client_id = task.predecessor.split(':')[0]

    elif task.predecessor:
        # task is a globalindex object -> predecessor is a globalindex obj too
        issuer_client_id = task.predecessor.client_id

    else:
        issuer_client_id = task.client_id

    issuer_client_title = info.get_client_by_id(issuer_client_id).title

    return '%s / %s' % (issuer_client_title, issuer)
