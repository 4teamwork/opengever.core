from opengever.contact import _
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import email_helper
from Products.CMFPlone.utils import safe_unicode
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def linked(item, value):
    return _render_link(item, value, include_css_class=True)


def linked_no_icon(item, value):
    return _render_link(item, value)


def _render_link(item, value, include_css_class=False):
    """Render a link to item with value as text.

    Optionally include an additional css class provided by the item.

    Item can be anything from brain to solr-document and those do not guarantee
    unicode strings. Thus we consider this method to be at the application
    boundary and make sure we work with unicode internally.
    """
    value = safe_unicode(value) if value else u''

    href = u'#'
    if hasattr(item, 'getURL'):
        href = item.getURL()
    elif hasattr(item, 'absolute_url'):
        href = item.absolute_url()
    href = safe_unicode(href)

    css_classes = [u'linkWrapper']
    if include_css_class:
        css_class = getattr(item, 'css_icon_class', None)
        if css_class is not None:
            css_classes.append(safe_unicode(css_class))

    anchor = u'<a href="%s">%s</a>' % (href, value)
    wrapper = u'<span class="%s">%s</span>' % (u" ".join(css_classes), anchor)
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
