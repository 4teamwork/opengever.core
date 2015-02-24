from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.activity.browser.resolve import ResolveNotificationView
from opengever.activity.models.notification import Notification
from opengever.ogds.base.actor import Actor
from opengever.activity import _
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.base import BaseTableSource
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface


def resolve_notification_link(item, value):
    return u'<a href="{}">{}</a>'.format(
        ResolveNotificationView.url_for(item.notification_id),
        item.activity.title)


def readable_actor(item, value):
    return Actor.lookup(item.activity.actor_id).get_label()


def translated_kind(item, value):
    return translate(item.activity.kind, domain='plone', context=getRequest())


class INotificationTableSourceConfig(ITableSourceConfig):
    """Marker interface for notification table source configs."""


class NotificationListingTab(BaseListingTab):
    implements(INotificationTableSourceConfig)

    model = Notification

    columns = (
        {'column': 'kind',
         'column_title': _(u'column_kind', default=u'Kind'),
         'transform': translated_kind},

        {'column': '',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': resolve_notification_link},

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
