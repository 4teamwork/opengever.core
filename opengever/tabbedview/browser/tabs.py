from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile     
from ftw.tabbedview.browser.views import BaseListingView
from ftw.tabbedview.interfaces import ITabbedView
from five import grok
from ftw.table import helper


class OpengeverListingTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')
    
    update = BaseListingView.update
    
    columns = (
                ('', helper.draggable),
                ('', helper.path_checkbox),
                ('Title', 'sortable_title', helper.linked),
                ('modified', helper.readable_date), 
                'Creator'
               )
    
    @property
    def view_name(self):
         return self.__name__.split('tabbedview_view-')[1]
              
    search_index = 'SearchableText' #only 'SearchableText' is implemented for now
    sort_on = 'modified'
    sort_order = 'reverse'    

class OpengeverTab(object):
    pass

class Documents(OpengeverListingTab):
    grok.name('tabbedview_view-documents')
    
    types = ['opengever.document.document',]
    
class Dossiers(OpengeverListingTab):
    grok.name('tabbedview_view-dossiers')
    
    types = ['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',]

class Tasks(OpengeverListingTab):
    grok.name('tabbedview_view-tasks')

    types = ['dummy.task',]
    
class Events(OpengeverListingTab):
    grok.name('tabbedview_view-events')

    types = ['dummy.event',]

from zope.annotation.interfaces import IAnnotations, IAnnotatable
from ftw.journal.interfaces import IAnnotationsJournalizable, IWorkflowHistoryJournalizable
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from ftw.table.interfaces import ITableGenerator
from zope.component import queryUtility
from ftw.table import helper
         
class Journal(grok.View, OpengeverTab):
     grok.context(IDossierMarker)
     grok.name('tabbedview_view-journal')
     grok.template('journal')
     
     def table(self):
         generator = queryUtility(ITableGenerator, 'ftw.tablegenerator') 
         columns = (('title', lambda x,y: x['action']['title']), 
                    'actor', 
                    ('time', helper.readable_date),
                    'comment'
                    )
         return generator.generate(reversed(self.data()), columns, css_mapping={'table':'journal-listing'})
     
     def data(self):
         context = self.context
         history = []
         
         if IAnnotationsJournalizable.providedBy(self.context):
             annotations = IAnnotations(context)
             return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
         elif IWorkflowHistoryJournalizable.providedBy(self.context):
             raise NotImplemented

        