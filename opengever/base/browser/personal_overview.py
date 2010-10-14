from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table import helper
from opengever.base import _
from opengever.base.browser.helper import client_title_helper
from opengever.globalindex.utils import indexed_task_link_helper
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tabs import Documents, Dossiers
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author
from opengever.task.helper import task_type_helper
from sqlalchemy import or_
from zope.component import getUtility
from zope.interface import Interface


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


class PersonalOverview(TabbedView):
    """The personal overview view show all documents and dossier
    where the actual user is the responsible.
    """

    def get_tabs(self):
        return (
            {'id': 'mytasks', 'icon': None, 'url': '#', 'class': None},
            {'id': 'mydossiers', 'icon': None, 'url': '#', 'class': None},
            {'id': 'mydocuments', 'icon': None, 'url': '#', 'class': None},
            {'id': 'issuedtasks', 'icon': None, 'url': '#', 'class': None},
            )


class MyDossiers(Dossiers):
    grok.name('tabbedview_view-mydossiers')
    grok.require('zope2.View')
    grok.context(Interface)

    types = ['opengever.dossier.businesscasedossier',
             'opengever.dossier.projectdossier',]

    search_options = {'responsible': authenticated_member,}

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyDocuments(Documents):
    grok.name('tabbedview_view-mydocuments')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'Creator': authenticated_member,
                      'isWorkingCopy': 0,
                      'trashed': False}


    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyTasks(OpengeverListingTab):
    """A listing view,
    wich show all task where the actual user is the responsible.

    This listing is based on opengever.globalindex (sqlalchemy) and respects
    the basic features of tabbedview such as searching and batching.
    """

    grok.name('tabbedview_view-mytasks')
    grok.require('zope2.View')
    grok.context(Interface)

    sort_on = 'modified'
    sort_order = 'reverse'

    enabled_actions = []
    major_actions = []

    columns = (

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

    def _get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_responsible_query(userid,
                                                           self.sort_on,
                                                           self.sort_order)

    def search(self, kwargs):
        """Override search method using SQLAlchemy queries from contact
        information utility.
        """

        query = self._get_base_query()

        # search / filter
        search_term = kwargs.get('SearchableText')
        if search_term:
            # do not use the catalogs default wildcards
            if search_term.endswith('*'):
                search_term = search_term[:-1]
            query = self._advanced_search_query(query, search_term)

        full_length = query.count()

        # respect batching
        start = self.pagesize * (self.pagenumber - 1)
        query = query.offset(start)
        query = query.limit(self.pagesize)

        result_length = query.count()

        self.contents = list(xrange(start)) + query.all() + \
            list(xrange(full_length - start - result_length))

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


class IssuedTasks(MyTasks):
    """A listing view, which show all task issued by the actual user.
    Based in MyTasks which implements tabbedview features with sqlalchemy.
    """

    grok.name('tabbedview_view-issuedtasks')

    def _get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_issuer_query(userid,
                                                      self.sort_on,
                                                      self.sort_order)


class AssignedTasks(MyTasks):
    """Lists all tasks assigned to this clients.
    Bases on MyTasks
    """

    grok.name('tabbedview_view-assignedtasks')

    def _get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_assigned_client_query(
            get_client_id(), self.sort_on, self.sort_order)
