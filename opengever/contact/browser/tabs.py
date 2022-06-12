from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.base.model import create_session
from opengever.contact import _
from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.models.team import Team
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import boolean_helper
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


def linked_title_helper(item, value):
    """Helper for linking the value with the team details view.
    """
    url = '{}/team-{}/view'.format(get_contactfolder_url(), item.team_id)
    return u'<a href="{}">{}</a>'.format(url, value)


class ITeamListingTableSourceConfig(ITableSourceConfig):
    """Marker interface for table source configuration using the OGDS team
    model as source.
    """


class ActiveOnlyFilter(Filter):
    """Filter to only display active teams."""

    def update_query(self, query):
        return query.filter(Team.active == True)  # noqa


class TeamsListing(BaseListingTab):
    """Tab registered on contacts folder listing all teams.
    """

    implements(ITeamListingTableSourceConfig)

    sort_on = 'title'
    sort_order = ''

    # the model attributes is used for a dynamic textfiltering functionality
    model = Team
    show_selects = False

    filterlist_name = 'team_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', _('label_tabbedview_filter_all')),
        ActiveOnlyFilter('filter_active', _('Active'), default=True))

    columns = (
        {'column': 'title',
         'column_title': _(u'label_title', default=u'Title'),
         'transform': linked_title_helper},

        {'column': 'groupid',
         'column_title': _(u'label_group', default=u'Group'),
         'transform': lambda item, value: item.group.label()},

        {'column': 'org_unit_id',
         'column_title': _(u'label_org_unit', default=u'Org Unit'),
         'transform': lambda item, value: item.org_unit.title},

        {'column': 'active',
         'column_title': _(u'label_active', default=u'Active'),
         'transform': boolean_helper}

    )

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        session = create_session()
        return session.query(Team)


@implementer(ITableSource)
@adapter(ITeamListingTableSourceConfig, Interface)
class TeamsListingTableSource(SqlTableSource):
    """Table source teams.
    """

    searchable_columns = [Team.title]
