from ftw.table import helper
from opengever.base.browser.helper import client_title_helper
from opengever.globalindex.model.task import Task
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.tabbedview import _
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author
from opengever.task.helper import task_type_helper
from sqlalchemy import or_
from zope.app.pagetemplate import ViewPageTemplateFile



def task_id_checkbox_helper(item, value):
    """ Checkbox helper based on tasks id attribute
    """

    attrs = {
        'type': 'checkbox',
        'class': 'noborder selectable',
        'name': 'task_ids:list',
        'id': item.task_id,
        'value': item.task_id,
        'title': 'Select %s' % item.title,
        }

    return '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                      for k, v in attrs.items()])


class GlobalTaskListingMixin(object):
    """A tabbed view mixing which brings support for listing tasks from
    the SQL (globally over all clients).

    There is support for searching, batching and ordering.

    Usage:
    Create tab-class subclassing this class and the OpengeverListingTab:

    >>> from opengever.globalindex.interfaces import ITaskQuery
    >>> class MyTaskListing(GlobalTaskListingMixin, OpengeverListingTab):
    ...     grok.name('tabbedview_view-globaltasks')
    ...     grok.require('Permission')
    ...
    ...     def get_base_query(self):
    ...         query_util = getUtility(ITaskQuery)
    ...         return query_util._get_some_tasks_query()
    """

    sort_on = 'modified'
    sort_order = 'reverse'

    enabled_actions = []
    major_actions = []

    select_all_template = ViewPageTemplateFile('select_all_globaltasks.pt')

    columns = (

        ('', task_id_checkbox_helper),

        {'column': 'review_state',
         'column_title': _(u'column_review_state', default=u'Review state'),
         'transform': helper.translated_string()},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': indexed_task_link_helper},

        {'column': 'task_type',
         'column_title': _(u'column_task_type', default=u'Task type'),
         'transform': task_type_helper},

        {'column': 'deadline',
         'column_title': _(u'column_deadline', default=u'Deadline'),
         'transform': helper.readable_date},

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

        {'column': 'client_id',
         'column_title': _('column_client', default=u'Client'),
         'transform': client_title_helper},

        {'column': 'sequence_number',
         'column_title': _(u'column_sequence_number',
                           default=u'Sequence number')},

        )

    def get_base_query(self):
        """This method must be implement. It has to return a SQLAlchemy
        query object on Task. See the ITaskQuery for further details.
        """
        raise NotImplemented

    def search(self, kwargs):
        """Override search method using SQLAlchemy queries from contact
        information utility.
        """

        query = self.get_base_query()

        # search / filter
        search_term = kwargs.get('SearchableText')
        if search_term:
            # do not use the catalogs default wildcards
            if search_term.endswith('*'):
                search_term = search_term[:-1]
            query = self._advanced_search_query(query, search_term)

        self.contents = query.all()

        self.len_results = len(self.contents)

    def _advanced_search_query(self, query, search_term):
        """Extend the given sql query object with the filters for searching
        for the search_term in all visible columns.
        When searching for multiple words the are splitted up and search
        seperately (otherwise a search like "Boss Hugo" would have no results
        because firstname and lastname are stored in seperate columns.)
        """

        model = Task

        # first lets lookup what fields (= sql columns) we have
        fields = []
        for column in self.columns:
            colname = column['column']

            # do not support dates
            if column.get('transform') == helper.readable_date:
                continue

            if colname == 'fullname':
                fields.append(model.firstname)
                fields.append(model.lastname)

            else:
                field = getattr(model, colname, None)
                if field:
                    fields.append(field)

        # lets split up the search term into words, extend them with the
        # default wildcards and then search for every word seperately
        for word in search_term.strip().split(' '):
            term = '%%%s%%' % word

            query = query.filter(or_(*[field.like(term) for field in fields]))

        return query
