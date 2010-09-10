from five import grok
from Products.CMFCore.utils import getToolByName
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from ftw.table import helper
from opengever.tabbedview.helper import readable_ogds_author
from opengever.dossier import _


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


class DossierOverview(OpengeverListingTab):
    """ Standard Listing Tabs for Tasklistings """
    grok.name('tabbedview_view-dossieroverview')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('reference_number', 'reference_number'),
        ('Title', 'sortable_title', linked),
        ('review_state', 'review_state', helper.translated_string()),
        {'column': 'responsible',
        'column_title': _(u'label_responsible_task', 'Responsible'),
        'transform': readable_ogds_author},
        ('start', 'start', helper.readable_date),
        ('end', 'end', helper.readable_date),
        )

    def search(self, kwargs):
        catalog = getToolByName(self.context,'portal_catalog')
        self.contents = catalog({'portal_type':'opengever.dossier.businesscasedossier'})#**kwargs)
        self.len_results = len(self.contents)
