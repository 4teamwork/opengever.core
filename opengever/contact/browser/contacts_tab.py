from opengever.contact import _
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import email_helper
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def linked(item, value):
    url_method = lambda: '#'
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url

    css_class = getattr(item, 'css_icon_class', '')

    if isinstance(value, unicode):
        value = value.encode('utf8')
    link = '<a href="%s">%s</a>' % (
        url_method(),
        value or '')
    wrapper = '<span class="linkWrapper %s">%s</span>' % (css_class, link)
    return wrapper


def linked_no_icon(item, value):
    url_method = lambda: '#'
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    link = u'<a href="%s" >%s</a>' % (
        url_method(),
        value and value or '')
    wrapper = u'<span class="linkWrapper">%s</span>' % link
    return wrapper


class Contacts(BaseCatalogListingTab):

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
    sort_order = ''

    show_selects = False
    enabled_actions = []
    major_actions = []
    selection = ViewPageTemplateFile("templates/no_selection_amount.pt")

    def update_config(self):
        super(BaseCatalogListingTab, self).update_config()

        # configuration for the extjs grid
        extjs_conf = {'auto_expand_column': 'lastname'}
        if isinstance(self.table_options, dict):
            self.table_options.update(extjs_conf)
        elif self.table_options is None:
            self.table_options = extjs_conf.copy()
