from five import grok
from plone.directives import form, dexterity
from opengever.tabbedview.browser.tabs import OpengeverTab, OpengeverListingTab
from ftw.table import helper
from opengever.tabbedview.browser.tabs import OpengeverSolrListingTab
from opengever.base import MessageFactory as _


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

class IWorkspace(form.Schema):
    pass        

class WorkspaceDossiers(OpengeverSolrListingTab):
    grok.context(IWorkspace)
    grok.name('tabbedview_view-dossiers')
    grok.template('generic')
    types = ['opengever.dossier.businesscasedossier','opengever.dossier.projectdossier',]

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', linked),
        ('review_state', 'review_state', helper.translated_string()),
        ('responsible'),#, helper.readable_author),
        ('start'),#) helper.readable_date),
        ('end'),# helper.readable_date),

        )
    search_options = {'responsible': authenticated_member,}

class WorkspaceDocuments(OpengeverSolrListingTab):
    grok.context(IWorkspace)
    grok.name('tabbedview_view-documents')
    grok.template('generic')
    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('document_author', 'document_author'),
        ('document_date', 'document_date', ),#helper.readable_date),
        ('receipt_date', 'receipt_date', ),#helper.readable_date),
        ('delivery_date', 'delivery_date', ),#helper.readable_date),
        ('checked_out', 'checked_out', helper.readable_author)
        )
    types = ['opengever.document.document', ]
    search_options = {'Creator': authenticated_member,}
    