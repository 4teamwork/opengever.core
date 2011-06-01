from five import grok
from opengever.contact import _
from opengever.tabbedview.browser.tabs import OpengeverCatalogListingTab
from opengever.tabbedview.helper import email_helper
from plone.dexterity.interfaces import IDexterityContainer
from zope.app.pagetemplate import ViewPageTemplateFile


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def linked(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url

    css_class = getattr(item, 'css_icon_class', '')

    link = '<a href="%s">%s</a>' % (
        url_method(),
        value and value.encode('utf-8') or '')
    wrapper = '<span class="linkWrapper %s">%s</span>' % (css_class, link)
    return wrapper


def linked_no_icon(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    link = u'<a href="%s" >%s</a>' % (
        url_method(),
        value and value or '')
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper


class Contacts(OpengeverCatalogListingTab):
    """ Listing of all Task of the authenticated Member """

    grok.name('tabbedview_view-local')
    grok.context(IDexterityContainer)

    types = ['opengever.contact.contact', ]

    columns = (
        {'column': 'lastname',
         'column_title': _(u'label_lastname',
                           default=u'Lastname'),
         'transform': linked},

        {'column': 'firstname',
         'column_title': _(u'label_firstname',
                           default=u'Firstname'),
         'transform': linked_no_icon},

        {'column': 'email',
         'column_title': _(u'label_email',
                           default=u'email'),
         'transform': email_helper},

        {'column': 'phone_office',
         'column_title': _(u'label_phone_office',
                           default=u'Phone office')},
        )

    sort_on = 'lastname'
    sort_order=''

    show_selects= False
    enabled_actions = []
    major_actions = []
    selection = ViewPageTemplateFile("no_selection_amount.pt")

    def update_config(self):
        OpengeverCatalogListingTab.update_config(self)

        # configuration for the extjs grid
        extjs_conf = {'auto_expand_column':'lastname'}
        if isinstance(self.table_options, dict):
            self.table_options.update(extjs_conf)
        elif self.table_options is None:
            self.table_options = extjs_conf.copy()
