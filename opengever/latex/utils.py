from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
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
        for id in ids:
            task = mapping.get(str(id))
            if task:
                yield task

    else:
        # empty generator
        pass


def get_dossier_sequence_number_and_title(item):
    """Returns the sequence number and title of the parent dossier of
    the item. `item` may be a brain or a sqlalchemy task object.
    """

    try:
        # brain?
        item.getPath()
    except AttributeError:
        is_brain = False
    else:
        is_brain = True

    if is_brain:
        dossier = item.getObject()

        while not IDossierMarker.providedBy(dossier):
            if IPloneSiteRoot.providedBy(dossier):
                return ('', '')
            dossier = aq_parent(aq_inner(dossier))

        sequence_number = getUtility(ISequenceNumber).get_number(dossier)
        title = dossier.Title()

    else:
        # sqlalchemy task object
        sequence_number = item.dossier_sequence_number
        if item.breadcrumb_title:
            title = item.breadcrumb_title.split(' > ')[-2]
        else:
            title = u''

    if isinstance(title, unicode):
        title = title.encode('utf-8')

    return str(sequence_number), title
