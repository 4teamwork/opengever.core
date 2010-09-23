from five import grok
from Products.CMFCore.utils import getToolByName
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from ftw.table import helper
from opengever.tabbedview.helper import readable_ogds_author, \
    readable_date_set_invisibles

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


class Contacts(OpengeverListingTab):
    """ Listing of all Task of the authenticated Member """

    grok.name('tabbedview_view-contacts')

    types = ['opengever.contact.contact', ]

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('email'),
        ('phone_office'),
        )

    sort_on = 'sortable_title'
    sort_order='asc'


