from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.ogds.base import _
from opengever.ogds.base.model.user import User
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
from sqlalchemy import asc, desc, or_
from five import grok


def linked_value_helper(item, value):
    """Helper for linking the value with the user profile.
    """

    info = getUtility(IContactInformation)
    url = info.get_profile_url(getattr(item, 'userid', None))

    if url:
        return '<a href="%s">%s</a>' % (url, value)
    else:
        return value


def email_helper(item, value):
    if value:
        return '<a href="mailto:%s">%s</a>' % (value, value)
    else:
        return ''


class UsersListing(OpengeverListingTab):
    """Tab registered on contacts folder (see opengever.contact) listing all
    users.
    """

    grok.name('tabbedview_view-users')
    grok.template('users')

    sort_on = 'lastname'
    sort_order = ''

    enabled_actions = []
    major_actions = []

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

        )

    def search(self, kwargs):
        """Override search method using SQLAlchemy queries from contact
        information utility.
        """

        info = getUtility(IContactInformation)
        query = info._users_query()

        # only display active users
        query = query.filter_by(active=True)

        # search / filter
        search_term = kwargs.get('SearchableText')
        if search_term:
            # do not use the catalogs default wildcards
            if search_term.endswith('*'):
                search_term = search_term[:-1]
            query = self._advanced_search_query(query, search_term)

        # sorting
        sort_on = kwargs.get('sort_on', UsersListing.sort_on)
        sort_order = kwargs.get('sort_order', UsersListing.sort_order)
        if sort_order.lower() in ('reverse', 'desc'):
            order = desc
        else:
            order = asc

        field = getattr(User, sort_on, None)
        if field:
            query = query.order_by(order(field))

        full_length = query.count()

        # respect batching
        start = self.pagesize * (self.pagenumber - 1)
        query = query.offset(start)
        query = query.limit(self.pagesize)

        result_length = query.count()

        self.contents = list(xrange(start)) + query.all() + \
            list(xrange(full_length - start - result_length))

        self.len_results = len(self.contents)

    def _advanced_search_query(self, query, search_term):
        """Extend the given sql query object with the filters for searching
        for the search_term in all visible columns.
        When searching for multiple words the are splitted up and search
        seperately (otherwise a search like "Boss Hugo" would have no results
        because firstname and lastname are stored in seperate columns.)
        """

        model = User

        # first lets lookup what fields (= sql columns) we have
        fields = []
        for column in self.columns:
            colname = column['column']

            field = getattr(model, colname, None)
            if field:
                fields.append(field)

        # lets split up the search term into words, extend them with the
        # default wildcards and then search for every word seperately
        for word in search_term.strip().split(' '):
            term = '%%%s%%' % word

            query = query.filter(or_(*[field.like(term) for field in fields]))

        return query
