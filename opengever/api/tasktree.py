from Acquisition import aq_parent
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.solr import OGSolrContentListing
from opengever.task.task import ITask
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
        return result

    def task_tree(self):
        main_task = self.context
        parent = aq_parent(main_task)
        while ITask.providedBy(parent):
            main_task = parent
            parent = aq_parent(main_task)

        solr = getUtility(ISolrSearch)
        filters = make_filters(
            path={
                'query': '/'.join(main_task.getPhysicalPath()),
                'depth': -1,
            },
            object_provides=ITask.__identifier__,
        )
        fieldlist = ['Title', 'portal_type', 'path', 'review_state']
        resp = solr.search(
            filters=filters, start=0, rows=1000, sort='created asc',
            fl=fieldlist)

        nodes = [
            {
                '@id': obj.getURL(),
                '@type': obj.PortalType(),
                'review_state': obj.review_state(),
                'title': obj.Title(),
            } for obj in OGSolrContentListing(resp)
        ]
        return make_tree_by_url(nodes, url_key='@id', children_key='children')


class TaskTreeGet(Service):
    def reply(self):
        tasktree = TaskTree(self.context, self.request)
        return tasktree(expand=True)["tasktree"]
