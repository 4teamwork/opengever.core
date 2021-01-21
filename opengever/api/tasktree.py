from Acquisition import aq_parent
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.solr import OGSolrContentListing
from opengever.task import TASK_STATE_PLANNED
from opengever.task.task import ITask
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
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

    def __call__(self, expand=False):
        result = {
            "tasktree": {
                "@id": "{}/@tasktree".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result
        result['tasktree']['children'] = self.task_tree()
        result['tasktree']['is_task_addable_in_main_task'] = self.is_task_addable_in_main_task()
        return result

    def is_task_addable_in_main_task(self):
        main_task = self.get_main_task()
        for fti in main_task.allowedContentTypes():
            if fti.id == main_task.portal_type:
                return True
        return False

    def is_task_addable_before(self, obj):
        return (obj.review_state() == TASK_STATE_PLANNED) and self.is_task_addable_in_main_task()

    def get_main_task(self):
        main_task = self.context
        parent = aq_parent(main_task)
        while ITask.providedBy(parent):
            main_task = parent
            parent = aq_parent(main_task)
        return main_task

    def task_tree(self):
        main_task = self.get_main_task()
        solr = getUtility(ISolrSearch)
        is_sequential = IFromSequentialTasktemplate.providedBy(main_task)
        filters = make_filters(
            path={
                'query': '/'.join(main_task.getPhysicalPath()),
                'depth': -1,
            },
            object_provides=ITask.__identifier__,
        )
        fieldlist = ['Title', 'portal_type', 'path', 'review_state']
        sort = 'getObjPositionInParent asc' if is_sequential else 'created asc'
        resp = solr.search(
            filters=filters, start=0, rows=1000, sort=sort,
            fl=fieldlist)

        nodes = []
        for obj in OGSolrContentListing(resp):
            child = {
                '@id': obj.getURL(),
                '@type': obj.PortalType(),
                'review_state': obj.review_state(),
                'title': obj.Title(),
            }
            if is_sequential:
                child['is_task_addable_before'] = self.is_task_addable_before(obj)
            nodes.append(child)

        return make_tree_by_url(nodes, url_key='@id', children_key='children')


class TaskTreeGet(Service):
    def reply(self):
        tasktree = TaskTree(self.context, self.request)
        return tasktree(expand=True)["tasktree"]
