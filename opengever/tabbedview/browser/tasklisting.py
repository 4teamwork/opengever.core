from five import grok
from ftw.journal.interfaces import IJournalizable
from ftw.table import helper
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.globalindex.model.task import Task
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import _
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.filters import PendingTasksFilter
from opengever.tabbedview.helper import display_org_unit_title_condition
from opengever.tabbedview.helper import linked_containing_maindossier
from opengever.tabbedview.helper import org_unit_title_helper
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.tabbedview.helper import workflow_state
from opengever.task.helper import task_type_helper
from sqlalchemy import and_, or_
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.interface import Interface


class IGlobalTaskTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configurations using the
    `opengever.globalindex` as source.
    """


class GlobalTaskListingTab(BaseListingTab):
    """A tabbed view mixin which brings support for listing tasks from
    the SQL (globally over all clients).

    There is support for searching, batching and ordering.
    """

    implements(IGlobalTaskTableSourceConfig)

    grok.context(IJournalizable)
    grok.require('zope2.View')

    template = ViewPageTemplateFile("generic_with_filters.pt")

    sort_on = 'modified'
    sort_reverse = False
    #lazy must be false otherwise there will be no correct batching
    lazy = False

    # the model attribute is used for a dynamic textfiltering functionality
    model = Task
    enabled_actions = []
    major_actions = []

    select_all_template = ViewPageTemplateFile('select_all_globaltasks.pt')

    filterlist_name = 'task_state_filter'
    filterlist_available = True

    filterlist = FilterList(
        Filter('filter_all', _('label_tabbedview_filter_all')),
        PendingTasksFilter('filter_pending',
                           _('label_pending', 'Pending'), default=True),
    )

    columns = (
        {'column': '',
         'sortable': False,
         'transform': task_id_checkbox_helper,
         'width': 30},

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
         'transform': lambda task, deadline: task.get_deadline_label()},

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
         'transform': helper.readable_date},

        {'column': 'containing_dossier',
         'column_title': _('containing_dossier', 'Dossier'),
         'transform': linked_containing_maindossier},

        {'column': 'issuing_org_unit',
         'column_title': _('column_issuing_org_unit',
                           default=u'Organisational Unit'),
         'transform': org_unit_title_helper,
         'condition': display_org_unit_title_condition},

        {'column': 'sequence_number',
         'column_title': _(u'column_sequence_number',
                           default=u'Sequence number')},

        )


class GlobalTaskTableSource(SqlTableSource):
    """Source adapter for Tasks we got from SQL
    """

    grok.implements(ITableSource)
    grok.adapts(IGlobalTaskTableSourceConfig, Interface)

    searchable_columns = [Task.title, Task.text,
                          Task.sequence_number, Task.responsible]

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """
        # initalize config
        query = super(GlobalTaskTableSource, self).build_query()

        query = self.avoid_duplicates(query)
        return query

    def avoid_duplicates(self, query):
        """If a task has a successor task, list only one of them.

        List only the one which is assigned to this client.
        """
        query = query.filter(
            or_(
                and_(Task.predecessor == None, Task.successors == None),
                Task.admin_unit_id == get_current_admin_unit().id()))
        return query
