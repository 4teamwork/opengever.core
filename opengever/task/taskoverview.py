from five import grok
from Products.CMFCore.utils import getToolByName
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from ftw.table import helper
from opengever.tabbedview.helper import readable_ogds_author, readable_date_set_invisibles

from opengever.task import _

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

class MyTasks(OpengeverListingTab):
    grok.name('tabbedview_view-mytasks')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', 'sortable_title', linked),
        {'column' : 'task_type', 
        'column_title' : _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', readable_date_set_invisibles), # erledigt am
        {'column' : 'responsible', 
        'column_title' : _(u'label_responsible_task', 'Responsible'),  
        'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created', 
        'column_title' : _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date },
        )

    types = ['opengever.task.task', ]

    search_options = {'responsible': authenticated_member}

    def search(self, kwargs):

        catalog = getToolByName(self.context,'portal_catalog')
        self.contents = catalog(**kwargs)
        self.len_results = len(self.contents)

class IssuedTasks(OpengeverListingTab):
    grok.name('tabbedview_view-issuedtasks')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', 'sortable_title', linked),
        {'column' : 'task_type', 
        'column_title' : _(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', readable_date_set_invisibles), # erledigt am
        {'column' : 'responsible', 
        'column_title' : _(u'label_responsible_task', 'Responsible'),  
        'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created', 
        'column_title' : _(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date },
        )


    types = ['opengever.task.task', ]

    search_options = {'issuer': authenticated_member}
        
    def search(self, kwargs):
        catalog = getToolByName(self.context,'portal_catalog')
        self.contents = catalog(**kwargs)
        self.len_results = len(self.contents)
