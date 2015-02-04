from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.model import Member
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.base import BaseTableSource
from zope.interface import implements
from zope.interface import Interface


class IMemberTableSourceConfig(ITableSourceConfig):
    """Marker interface for member table source configs."""


class MemberListingTab(BaseListingTab):
    implements(IMemberTableSourceConfig)

    model = Member

    columns = (
        {'column': 'firstname',
         'column_title': _(u'column_firstname', default=u'Firstname'),
         },

        {'column': 'lastname',
         'column_title': _(u'column_lastname', default=u'Lastname'),
         },

        {'column': 'email',
         'column_title': _(u'column_email', default=u'E-Mail'),
         },
        )

    def get_base_query(self):
        return Member.query


class MemberTableSource(BaseTableSource):
    grok.implements(ITableSource)
    grok.adapts(MemberListingTab, Interface)

    searchable_columns = [Member.firstname, Member.lastname, Member.email]
