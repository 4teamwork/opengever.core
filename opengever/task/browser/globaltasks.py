from zope.component import getUtility
from opengever.globalindex.interfaces import ITaskQuery
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.tabbedview.browser.listing import BaseListingView
from ftw.table import helper
from opengever.tabbedview.helper import readable_ogds_author, \
    readable_date_set_invisibles
from opengever.task import _


class GlobalTaskOverview(TabbedView):

    def get_tabs(self):
        return (
            {'id': 'mytasks', 'icon': None, 'url': '#', 'class': None},
            {'id': 'issuedtasks', 'icon': None, 'url': '#', 'class': None},
            {'id': 'assignedtasks', 'icon': None, 'url': '#', 'class': None},
        )

class TaskBaseListing(BaseListingView):

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        #('Title', opengever_helper.solr_linked),
        {'column': 'title',
        'column_title': _(u'Title', 'Title')},
        #{'column': 'task_type',
        #'column_title': _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        # erledigt am
        {'column': 'completed',
         'column_title': 'date_of_completion',
         'transform': readable_date_set_invisibles },
        #('date_of_completion', opengever_helper.readable_date_set_invisibles),
        {'column': 'responsible',
        'column_title': _(u'label_responsible_task', 'Responsible'),
        'transform': readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column': 'created',
        'column_title': _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date},
        {'column': 'client_id',
         'column_title': _('client_id', 'Client')},
        #{'column': 'sequence_number',
        # 'column_title': _(u'sequence_number', "Sequence Number")},
         )

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


    def update(self):
        self.search()

    @property
    def batch(self):
        return self.contents

    @property
    def multiple_pages(self):
        return False
        
class MyTasks(TaskBaseListing):

    def search(self):
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        userid = portal_state.member().getId()
        query_util = getUtility(ITaskQuery)
        self.contents = query_util.get_tasks_for_responsible(userid)
        self.len_results = len(self.contents)

class IssuedTasks(TaskBaseListing):
    """
    """
    def search(self):
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        userid = portal_state.member().getId()
        query_util = getUtility(ITaskQuery)
        self.contents = query_util.get_tasks_for_issuer(userid)
        self.len_results = len(self.contents)
    # def build_query(self):
    #     aid = authenticated_member(self.context)
    #     return 'portal_type:opengever.task.task AND issuer:%s AND \
    #             ! responsible:%s' % (aid, aid)


class AssignedTasks(TaskBaseListing):
    """
    """
    # def search(self):
    #     
    #     
    # def build_query(self):
    #     client_id = get_client_id()
    #     return 'portal_type:opengever.task.task AND assigned_client:(%s)' % (
    #         client_id)