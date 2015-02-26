from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Member
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


class IMemberTableSourceConfig(ITableSourceConfig):
    """Marker interface for member table source configs."""


class MemberListingTab(BaseListingTab):
    implements(IMemberTableSourceConfig)

    model = Member

    @property
    def columns(self):
        return (
            {'column': 'firstname',
             'column_title': _(u'column_firstname', default=u'Firstname'),
             'transform': self.get_firstname_link,
             },

            {'column': 'lastname',
             'column_title': _(u'column_lastname', default=u'Lastname'),
             'transform': self.get_lastname_link,
             },

            {'column': 'email',
             'column_title': _(u'column_email', default=u'E-Mail'),
             },
            )

    def get_firstname_link(self, item, value):
        return item.get_firstname_link(self.context)

    def get_lastname_link(self, item, value):
        return item.get_lastname_link(self.context)

    def get_base_query(self):
        return Member.query


class MemberTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(MemberListingTab, Interface)

    searchable_columns = [Member.firstname, Member.lastname, Member.email]
