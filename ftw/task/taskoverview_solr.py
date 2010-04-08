from five import grok
from opengever.tabbedview.browser.tabs import OpengeverListingTab, OpengeverSolrListingTab
from zope.component import queryUtility, getUtility
from ftw.table import helper
from opengever.tabbedview import helper as opengever_helper
from opengever.tabbedview.helper import readable_ogds_author
from opengever.octopus.tentacle.contacts import ContactInformation
from opengever.octopus.tentacle.interfaces import ITentacleConfig

from ftw.task import _

def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()
    

class MyTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-mytasks_solr')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', helper.solr_linked),
        {'column' : 'task_type', 
        'column_title' : _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', opengever_helper.readable_date_set_invisibles), # erledigt am
        {'column' : 'responsible', 
        'column_title' : _(u'label_responsible_task', 'Responsible'),  
        'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created', 
        'column_title' : _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date },
        )

    types = ['ftw.task.task', ]
    
    search_options = {'responsible': authenticated_member}


class IssuedTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-issuedtasks_solr')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', helper.solr_linked),
        {'column' : 'task_type', 
        'column_title' : _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', opengever_helper.readable_date_set_invisibles), #erledigt am
        {'column' : 'responsible', 
        'column_title' : _(u'label_responsible_task', 'Responsible'),  
        'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created', 
        'column_title' : _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date },
        )
    
    def build_query(self):
        aid = authenticated_member(self.context)
        return 'portal_type:ftw.task.task AND issuer:%s AND ! responsible:%s' % (aid, aid)

        
class AssignedTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-assignedtasks_solr')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', helper.solr_linked),
        {'column' : 'task_type', 
        'column_title' : _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', opengever_helper.readable_date_set_invisibles), # erledigt am
        {'column' : 'responsible', 
        'column_title' : _(u'label_responsible_task', 'Responsible'),  
        'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created', 
        'column_title' : _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date },
        )

    def build_query(self):
        member = authenticated_member(self.context)
        conf = getUtility(ITentacleConfig)
        client_id = conf.cid
        return 'portal_type:ftw.task.task AND assigned_client:(%s)' % client_id
