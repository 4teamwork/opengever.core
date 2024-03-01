from Acquisition import aq_parent
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from ftw.solr.query import make_path_filter
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.solr import OGSolrContentListing
from opengever.task import TASK_STATE_PLANNED
from opengever.task.task import ITask
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(ITask, IOpengeverBaseLayer)
class TaskTree(object):
    """A tree representing the task hierarchy
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.solr = getUtility(ISolrSearch)
        self.fieldlist = [
            'Title', 'portal_type', 'path', 'review_state', 'object_provides',
            'has_sametype_children', 'responsible']

    def __call__(self, expand=False):
        result = {
            "tasktree": {
                "@id": "{}/@tasktree".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result
        result['tasktree']['children'] = self.task_tree()
        return result

    def is_task_addable_in_sequential_task_container(self, container):
        if not IContainSequentialProcess.providedBy(container):
            return False

        for fti in container.allowedContentTypes():
            if fti.id == container.portal_type:
                return True
        return False

    def is_task_addable_before(self, solr_item, parent_context):
        if IPartOfSequentialProcess.__identifier__ not in solr_item.object_provides \
                or not parent_context:
            return False
        return solr_item.review_state() == TASK_STATE_PLANNED \
            and self.is_task_addable_in_sequential_task_container(parent_context)

    def get_main_task(self):
        main_task = self.context
        parent = aq_parent(main_task)
        while ITask.providedBy(parent):
            main_task = parent
            parent = aq_parent(main_task)
        return main_task

    """For sequential processes we allow adding subtasks at specific positions
    in the process. For this we need to find out whether a given task contains
    a sequential process and tasks can be added in it, as well as whether a
    task can be added before a given task.

    For performance reasons we avoid retrieving the objects and work only
    with the solr-items whenever possible. But we need to lookup the obejct
    to check if we can add tasks to the contained process.
    This is of course never the case for leaf tasks, so we can restrict
    the object lookup to IContainProcess-tasks only. This reduces the object
    lookup to a minimum.
    """
    def extend_tree_with_addable_information(self, tree, solr_items_per_url, parent_context=None):
        solr_item = solr_items_per_url.get(tree.get('@id'))
        is_task_addable_before = self.is_task_addable_before(solr_item, parent_context)
        is_task_addable = False
        children = tree.get('children')
        if children:
            context = solr_item.getObject()
            is_task_addable = self.is_task_addable_in_sequential_task_container(context)

            for child in children:
                self.extend_tree_with_addable_information(child, solr_items_per_url, context)

        tree['is_task_addable_before'] = is_task_addable_before
        tree['is_task_addable'] = is_task_addable

    def recursive_query(self, item, docs):
        docs.append(item)
        if not item.get("has_sametype_children"):
            return
        filters = make_filters(
            path={
                'query': item.get("path"),
                'depth': 1,
            },
            object_provides=ITask.__identifier__,
        )
        is_sequential = IContainSequentialProcess.__identifier__ in item.get("object_provides")
        sort = 'getObjPositionInParent asc' if is_sequential else 'created asc'
        resp = self.solr.search(
            filters=filters, start=0, rows=1000, sort=sort, fl=self.fieldlist)
        for item in resp.docs:
            self.recursive_query(item, docs)

    def task_tree(self):
        main_task = self.get_main_task()
        path = '/'.join(main_task.getPhysicalPath())
        resp = self.solr.search(filters=make_path_filter(path, 0),
                                fl=self.fieldlist)

        if not resp.docs:
            return []
        docs = []
        if resp.docs:
            self.recursive_query(resp.docs[0], docs)
            resp.docs = docs

        nodes = []
        solr_items_per_url = {}
        for obj in OGSolrContentListing(resp):
            child = {
                '@id': obj.getURL(),
                '@type': obj.PortalType(),
                'review_state': obj.review_state(),
                'title': obj.Title(),
                'responsible_actor': serialize_actor_id_to_json_summary(
                    obj.get('responsible'))
            }
            solr_items_per_url[obj.getURL()] = obj
            nodes.append(child)

        tree = make_tree_by_url(nodes, url_key='@id', children_key='children')
        self.extend_tree_with_addable_information(tree[0], solr_items_per_url)
        return tree


class TaskTreeGet(Service):
    def reply(self):
        tasktree = TaskTree(self.context, self.request)
        return tasktree(expand=True)["tasktree"]
