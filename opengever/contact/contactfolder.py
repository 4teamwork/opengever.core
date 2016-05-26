from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.contact import _
from opengever.contact.interfaces import IContactFolder
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import email_helper
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityContainer
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class ContactFolder(Container, TranslatedTitleMixin):
    """Container which contains all contacts.
    """

    implements(IContactFolder)


    Title = TranslatedTitleMixin.Title


class ContactFolderAddForm(TranslatedTitleAddForm):
    grok.name('opengever.contact.contactfolder')


class ContactFolderEditForm(TranslatedTitleEditForm):
    grok.context(IContactFolder)


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def linked(item, value):
    url_method = lambda: '#'
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
    sort_order = ''

    show_selects = False
    enabled_actions = []
    major_actions = []
    selection = ViewPageTemplateFile("no_selection_amount.pt")

    def update_config(self):
        super(BaseCatalogListingTab, self).update_config()

        # configuration for the extjs grid
        extjs_conf = {'auto_expand_column': 'lastname'}
        if isinstance(self.table_options, dict):
            self.table_options.update(extjs_conf)
        elif self.table_options is None:
            self.table_options = extjs_conf.copy()
