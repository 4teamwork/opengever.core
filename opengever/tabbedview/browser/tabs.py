from ftw.tabbedview.browser.views import BaseListingView
from ftw.tabbedview.interfaces import ITabbedView
from five import grok
from ftw.table import helper


class OpengeverTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')
    
    update = BaseListingView.update
    
    columns = (('', helper.uid_checkbox),
              ('Title', helper.linked),
              ('modified', helper.readable_date), 
              'Creator')
              
    search_index = 'SearchableText'
    sort_on = 'sortable_title'
    sort_order = 'reverse'    

class Documents(OpengeverTab):
    grok.name('tabbedview_view-documents')
    
    types = ['opengever.document.document',]
    
class Dossiers(OpengeverTab):
    grok.name('tabbedview_view-dossiers')

    types = ['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',]


        