from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile     
from ftw.tabbedview.browser.views import BaseListingView
from ftw.tabbedview.interfaces import ITabbedView
from five import grok
from ftw.table import helper


class OpengeverTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')
    
    update = BaseListingView.update
    
    columns = (
                ('', helper.draggable),
               ('', helper.path_checkbox),
              ('Title','sortable_title', helper.linked),
              ('modified', helper.readable_date), 
              'Creator')
    
    @property
    def view_name(self):
         return self.__name__.split('tabbedview_view-')[1]
              
    search_index = 'SearchableText' #only 'SearchableText' is implemented for now
    sort_on = 'modified'
    sort_order = 'reverse'    

class Documents(OpengeverTab):
    grok.name('tabbedview_view-documents')
    
    types = ['opengever.document.document',]
    
class Dossiers(OpengeverTab):
    grok.name('tabbedview_view-dossiers')
    
    types = ['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',]


        