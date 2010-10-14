from zope.component import getUtility
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.utils import get_client_id
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.tabbedview.browser.listing import BaseListingView
from ftw.table import helper
from opengever.tabbedview.helper import readable_ogds_author, \
    readable_date_set_invisibles
from opengever.task import _


def globalindex_path_checkbox(item, value):
    return '<input type="checkbox" class="noborder" name="paths:list" id="%s" value="%s" alt="Select %s" title="Select %s">' % (item.task_id, item.physical_path,  item.title, item.title)

def globalindex_linked(context):
    """A helper method wich show the titel as a link.
    When the task is not on the actual client it open it in a new window."""
    actual_client = get_client_id()
    def get_linked(item, value):
        img = u'<img src="%s/%s"/>' % (context.portal_url(), item.icon)
        if actual_client == item.client_id:
            link = u'<a class="rollover-breadcrumb" href="%s" title="%s">%s%s</a>' % (item.physical_path,item.title, img, value)
        else:
            link = u'<a class="rollover-breadcrumb" target="_blank" href="%s" title="%s">%s%s</a>' % (item.physical_path,item.title, img, value)
        # " &gt; ".join(item['Title'] for i in item.breadcrumb_titles)
        item.physical_path
        wrapper = u'<span class="linkWrapper">%s</span>' % link
        return wrapper
    return get_linked

class TaskBaseListing(BaseListingView):

    def __init__(self, context, request):
        self.columns= (
            ('', globalindex_path_checkbox),
            ('review_state', 'review_state', helper.translated_string()),
            {'column': 'title',
            'column_title': _(u'Title', 'Title'),
            'transform': globalindex_linked(context)},
            {'column': 'task_type',
            'column_title': _(u'label_task_type', 'Task Type')},
            {'column': 'deadline',
             'column_title': _(u'label_deadline', 'Deadline'),
             'transform': helper.readable_date},
            {'column': 'completed',
             'column_title': _(u'date_of_completion'),
             'transform': readable_date_set_invisibles },
            {'column': 'responsible',
            'column_title': _(u'label_responsible_task', 'Responsible'),
            'transform': readable_ogds_author},
            ('issuer', readable_ogds_author),
            {'column': 'created',
            'column_title': _(u'label_issued_date', 'issued at'),
            'transform': helper.readable_date},
            {'column': 'client_id',
             'column_title': _('client_id', 'Client')},
            {'column': 'sequence_number',
             'column_title': _(u'sequence_number', "Sequence Number")},
             )
        self.sort_on = 'modified'
        self.sort_order = 'reverse'
        super(TaskBaseListing, self).__init__(context, request)

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


    def update(self):
        self.pagenumber = int(self.request.get('pagenumber', 1))
        if self.request.get('sort_on', None):
            self.sort_on = self.request.get('sort_on')[7:]
        self.sort_order = self.request.get('sort_order', self.sort_order)
        self.url = self.context.absolute_url()
        self.search()



