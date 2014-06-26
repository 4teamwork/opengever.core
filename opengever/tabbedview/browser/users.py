from five import grok
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.models.user import User
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.tabbedview.browser.listing import ListingView
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from opengever.tabbedview.helper import boolean_helper
from opengever.tabbedview.helper import email_helper
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface


def linked_value_helper(item, value):
    """Helper for linking the value with the user profile.
    """

    if not value:
        return ''

    info = getUtility(IContactInformation)
    url = info.get_profile_url(getattr(item, 'userid', None))

    if url:
        return '<a href="%s">%s</a>' % (url, value)
    else:
        return value


class IUsersListingTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configuration using the OGDS users
    model as source.
    """


class UsersListing(grok.View, OpengeverTab, ListingView):
    """Tab registered on contacts folder (see opengever.contact) listing all
    users.
    """

    implements(IUsersListingTableSourceConfig)

    grok.name('tabbedview_view-users')
    grok.context(Interface)
    grok.require('zope2.View')

    sort_on = 'lastname'
    sort_order = ''
    #lazy must be false otherwise there will be no correct batching
    lazy = False

    # the model attributes is used for a dynamic textfiltering functionality
    model = User
    show_selects = False
    enabled_actions = []
    major_actions = []
    selection = ViewPageTemplateFile("no_selection_amount.pt")

    columns = (
        {'column': 'lastname',
         'column_title': _(u'label_userstab_lastname',
                           default=u'Lastname'),
         'transform': linked_value_helper},

        {'column': 'firstname',
         'column_title': _(u'label_userstab_firstname',
                           default=u'Firstname'),
         'transform': linked_value_helper},

        {'column': 'userid',
         'column_title': _(u'label_userstab_userid',
                           default=u'Userid'),
         'transform': linked_value_helper},

        {'column': 'email',
         'column_title': _(u'label_userstab_email',
                           default=u'Email'),
         'transform': email_helper},

        {'column': 'phone_office',
         'column_title': _(u'label_userstab_phone_office',
                           default=u'Office Phone')},

        {'column': 'department',
         'column_title': _(u'label_department_user',
                          default=u'Department')},


        {'column': 'directorate',
         'column_title': _(u'label_directorate_user',
                         default=u'Directorate')},

        {'column': 'active',
         'column_title': _(u'label_active',
                           default=u'Active'),
         'transform': boolean_helper},

        )

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        info = getUtility(IContactInformation)
        return info._users_query()


class UsersListingTableSource(SqlTableSource):
    """Table source OGDS users.
    """

    grok.implements(ITableSource)
    grok.adapts(IUsersListingTableSourceConfig, Interface)
