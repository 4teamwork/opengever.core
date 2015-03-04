from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Committee
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


class ICommitteeTableSourceConfig(ITableSourceConfig):
    """Marker interface for committee table source configs."""


class CommitteeListingTab(BaseListingTab):
    implements(ICommitteeTableSourceConfig)

    model = Committee

    columns = (
        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': lambda item, value: item.get_link(),
         },
        )

    def get_base_query(self):
        return Committee.query.filter_by(
            admin_unit_id=get_current_admin_unit().id())


class CommitteeTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(CommitteeListingTab, Interface)

    searchable_columns = [Committee.title]
