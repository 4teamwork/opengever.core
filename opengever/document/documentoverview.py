from five import grok
from Products.CMFCore.utils import getToolByName
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from ftw.table import helper


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


class DocumentOverview(OpengeverListingTab):
    """ Standard Listing Tabs for Documentoverview """
    grok.name('tabbedview_view-documentoverview')
    
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('document_author', 'document_author'),
        ('document_date', 'document_date', helper.readable_date),
        ('receipt_date', 'receipt_date', helper.readable_date),
        ('delivery_date', 'delivery_date', helper.readable_date),
        )

    types = ['opengever.document.document', ]

    def search(self, kwargs):
        catalog = getToolByName(self.context,'portal_catalog')
        self.contents = catalog({'portal_type':'opengever.document.document'})#**kwargs)
        self.len_results = len(self.contents)
