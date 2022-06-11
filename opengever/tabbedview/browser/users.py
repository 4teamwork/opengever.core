from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.base.model import create_session
from opengever.ogds.base.actor import Actor
from opengever.ogds.models.user import User
from opengever.tabbedview import _
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import boolean_helper
from opengever.tabbedview.helper import email_helper
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


def linked_user_helper(item, value):
    """Helper for linking the value with the user profile.
    """
    userid = getattr(item, 'userid', None)
    url = Actor.user(userid, user=item).get_profile_url()
    if not url:
        return value
    return u'<a href="{}">{}</a>'.format(url, value)


class IUsersListingTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configuration using the OGDS users
    model as source.
    """


class ActiveOnlyFilter(Filter):
    """Filter to only display active users."""

    def update_query(self, query):
        return query.filter_by(active=True)


class UsersListing(BaseListingTab):
    """Tab registered on contacts folder (see opengever.contact) listing all
    users.
    """
    implements(IUsersListingTableSourceConfig)

    sort_on = 'lastname'
    sort_order = ''

    # the model attributes is used for a dynamic textfiltering functionality
    model = User
    show_selects = False

    filterlist_name = 'user_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', _('label_tabbedview_filter_all')),
        ActiveOnlyFilter('filter_active', _('Active'), default=True))

    columns = (
        {'column': 'lastname',
         'column_title': _(u'label_userstab_lastname',
                           default=u'Lastname'),
         'transform': linked_user_helper},

        {'column': 'firstname',
         'column_title': _(u'label_userstab_firstname',
                           default=u'Firstname'),
         'transform': linked_user_helper},

        {'column': 'userid',
         'column_title': _(u'label_userstab_userid',
                           default=u'Userid'),
         'transform': linked_user_helper},

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

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        session = create_session()
        return session.query(User)


@implementer(ITableSource)
@adapter(IUsersListingTableSourceConfig, Interface)
class UsersListingTableSource(SqlTableSource):
    """Table source OGDS users.
    """

    searchable_columns = [User.lastname, User.firstname, User.userid,
                          User.email, User.phone_office, User.department,
                          User.directorate]
