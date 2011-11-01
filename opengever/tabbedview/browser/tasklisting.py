from five import grok
from ftw.journal.interfaces import IJournalizable
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.base.browser.helper import client_title_helper
from opengever.globalindex.model.task import Task
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.tabbedview import _
from opengever.tabbedview.browser.listing import ListingView
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import overdue_date_helper
from opengever.tabbedview.helper import readable_date
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.tabbedview.helper import workflow_state
from opengever.task.helper import task_type_helper
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements, Interface
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource


class IGlobalTaskTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    `opengever.globalindex` as source.
    """


class GlobalTaskListingTab(grok.View, OpengeverTab,
                           ListingView):
    """A tabbed view mixing which brings support for listing tasks from
    the SQL (globally over all clients).

    There is support for searching, batching and ordering.
    """

    implements(IGlobalTaskTableSourceConfig)

    grok.context(IJournalizable)
    grok.require('zope2.View')

    sort_on = 'modified'
    sort_reverse = False
    #lazy must be false otherwise there will be no correct batching
    lazy = False

    # the model attributes is used for a dynamic textfiltering functionality
    model = Task
    enabled_actions = [
        'reset_tableconfiguration',
        ]
    major_actions = []

    select_all_template = ViewPageTemplateFile('select_all_globaltasks.pt')

    columns = (

        ('', task_id_checkbox_helper),

        {'column': 'review_state',
         'column_title': _(u'column_review_state', default=u'Review state'),
         'transform': workflow_state},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': indexed_task_link_helper},

        {'column': 'task_type',
         'column_title': _(u'column_task_type', default=u'Task type'),
         'transform': task_type_helper},

        {'column': 'deadline',
         'column_title': _(u'column_deadline', default=u'Deadline'),
         'transform': overdue_date_helper},

        {'column': 'completed',
         'column_title': _(u'column_date_of_completion',
                           default=u'Date of completion'),
         'transform': readable_date_set_invisibles},

        {'column': 'responsible',
         'column_title': _(u'label_responsible_task', default=u'Responsible'),
         'transform': readable_ogds_author},

        {'column': 'issuer',
         'column_title': _(u'label_issuer', default=u'Issuer'),
         'transform': readable_ogds_author},

        {'column': 'created',
         'column_title': _(u'column_issued_at', default=u'Issued at'),
         'transform': readable_date},

        {'column': 'client_id',
         'column_title': _('column_client', default=u'Client'),
         'transform': client_title_helper},

        {'column': 'sequence_number',
         'column_title': _(u'column_sequence_number',
                           default=u'Sequence number')},

        )

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__


class GlobalTaskTableSource(SqlTableSource):
    """Source adapter for Tasks we got from SQL
    """

    grok.implements(ITableSource)
    grok.adapts(IGlobalTaskTableSourceConfig, Interface)
