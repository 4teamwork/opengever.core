from ftw.tabbedview.browser.views import BaseListingView
from ftw.tabbedview.interfaces import ITabbedView
from five import grok
from ftw.table import helper


class OpengeverTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')
    
    update = BaseListingView.search
    
    columns = (('Title','sortable_title',), 
               ('modified','modified',helper.readable_date), 
               ('Creator','Creator',helper.readable_author),)    
    

class Documents(OpengeverTab):
    grok.name('tabbedview_view-documents')
    
    types = ['opengever.document.document',]
    
class Dossiers(OpengeverTab):
    grok.name('tabbedview_view-dossiers')

    types = ['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',]


        