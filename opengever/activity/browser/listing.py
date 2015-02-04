from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.activity.models.notification import Notification
from opengever.ogds.base.actor import Actor
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.base import BaseTableSource
from zope.interface import implements
from zope.interface import Interface


def mark_unread(item, value):
    if value:
        return ''
    else:
        return '<a href="#" class="mark_as_read"></a>'


def readable_actor(item, value):
    return Actor.lookup(item.activity.actor_id).get_label()


class INotificationTableSourceConfig(ITableSourceConfig):
    """Marker interface for notification table source configs."""


class NotificationListingTab(BaseListingTab):
    implements(INotificationTableSourceConfig)

    model = Notification

    columns = (
        {'column': 'read',
         'column_title': _(u'column_mark_read', default=u'Mark as read'),
         'transform': mark_unread},

        {'column': 'kind',
         'column_title': _(u'column_kind', default=u'Kind'),
         'transform': lambda item, value: item.activity.kind},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': lambda item, value: item.activity.render_link()},

        {'column': 'actor',
         'column_title': _(u'column_Actor', default=u'Actor'),
         'transform': readable_actor}
    )

    def get_base_query(self):
        return Notification.query


class NotificationTableSource(BaseTableSource):
    grok.implements(ITableSource)
    grok.adapts(NotificationListingTab, Interface)

    searchable_columns = []
