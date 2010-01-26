from five import grok
from opengever.tabbedview.browser.tabs import OpengeverListingTab, OpengeverSolrListingTab
from zope.component import queryUtility
from ftw.table import helper
from opengever.tabbedview import helper as opengever_helper


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()
    
def linked(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    img = u'<img src="%s"/>' % (item.getIcon)
    link = u'<a href="%s" >%s%s</a>' % (url_method(), img, value) 
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper
    

class MyTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-mytasks_solr')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', helper.solr_linked),
        ('deadline', helper.readable_date),
        ('date_of_completion', helper.readable_date), # erledigt am
        ('responsible', opengever_helper.readable_ogds_author),
        ('issuer', opengever_helper.readable_ogds_author), # zugewiesen von
        ('modified', helper.readable_date)# zugewiesem am
        )
    types = ['ftw.task.task', ]
    
    search_options = {'responsible': authenticated_member, 'review_state':'task-state-open'}
    


class IssuedTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-issuedtasks_solr')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', helper.solr_linked),
        ('deadline', helper.readable_date),
        ('date_of_completion', helper.readable_date), # erledigt am
        ('responsible', opengever_helper.readable_ogds_author),
        ('issuer', opengever_helper.readable_ogds_author), # zugewiesen von
        ('modified', helper.readable_date)# zugewiesem am
        )
    
    def build_query(self):
        aid = authenticated_member(self.context)
        return 'portal_type:ftw.task.task AND issuer:%s AND ! responsible:%s' % (aid, aid)
