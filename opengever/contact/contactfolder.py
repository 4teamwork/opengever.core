from five import grok
from opengever.tabbedview.browser.tabs import OpengeverCatalogListingTab
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import email_helper
from ftw.table import helper
from ftw.table.catalog_source import default_custom_sort
from opengever.contact import _
from plone.dexterity.interfaces import IDexterityContainer


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


class Contacts(OpengeverCatalogListingTab):
    """ Listing of all Task of the authenticated Member """

    grok.name('tabbedview_view-contacts')
    grok.context(IDexterityContainer)

    types = ['opengever.contact.contact', ]

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),

        {'column':'Title',
         'column_title':_('name', default='Name'),
         'sort_index' : 'sortable_title',
         'transform':linked},
         {'column':'email',
          'column_title':_('label_email', default="email"),
          'transform': email_helper,
          },
          {'column':'phone_office',
            'column_title':_('label_phone_office', default='Phone office')
          },
        )

    sort_on = 'sortable_title'
    sort_order='asc'

    def custom_sort(self, results, sort_on, sort_reverse):

        if sort_on in ('email', 'phone_office'):
            # we have not sort index, so sort manually

            return default_custom_sort(results, sort_on, sort_reverse)

        else:
            return OpengeverTab.custom_sort(self, results, sort_on, sort_reverse)
