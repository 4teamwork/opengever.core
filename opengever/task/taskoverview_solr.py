from five import grok
from opengever.tabbedview.browser.tabs import OpengeverSolrListingTab
from ftw.table import helper
from opengever.tabbedview import helper as opengever_helper
from opengever.tabbedview.helper import readable_ogds_author
from opengever.ogds.base.utils import get_client_id

from opengever.task import _


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


class TaskSolrListing(OpengeverSolrListingTab):

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', opengever_helper.solr_linked),
        {'column': 'task_type',
        'column_title': _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        # erledigt am
        ('date_of_completion', opengever_helper.readable_date_set_invisibles),
        {'column': 'responsible',
        'column_title': _(u'label_responsible_task', 'Responsible'),
        'transform': readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column': 'created',
        'column_title': _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date},
        {'column': 'client_id',
         'column_title': _('client_id', 'Client')},
        {'column': 'sequence_number',
         'column_title': _(u'sequence_number', "Sequence Number")},
         )

    types = ['opengever.task.task', ]


class MyTasks(TaskSolrListing):
    grok.name('tabbedview_view-mytasks_solr')

    search_options = {'responsible': authenticated_member}


class IssuedTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-issuedtasks_solr')

    def build_query(self):
        aid = authenticated_member(self.context)
        return 'portal_type:opengever.task.task AND issuer:%s AND \
                ! responsible:%s' % (aid, aid)


class AssignedTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-assignedtasks_solr')

    def build_query(self):
        client_id = get_client_id()
        return 'portal_type:opengever.task.task AND assigned_client:(%s)' % (
            client_id)
