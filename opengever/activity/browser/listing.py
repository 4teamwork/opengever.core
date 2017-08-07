from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.activity import _
from opengever.activity import notification_center
from opengever.activity.browser import resolve_notification_url
from opengever.ogds.base.actor import Actor
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import GeverTableSource
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


def resolve_notification_link(item, value):
    return u'<a href="{}">{}</a>'.format(
        resolve_notification_url(item).decode('ascii'),
        item.activity.title)


def readable_actor(item, value):
    return Actor.lookup(item.activity.actor_id).get_label()


def readable_date(item, date):
    return api.portal.get_localized_time(
        item.activity.created, long_format=True)


class INotificationTableSourceConfig(ITableSourceConfig):
    """Marker interface for notification table source configs."""


class NotificationListingTab(BaseListingTab):
    implements(INotificationTableSourceConfig)

    sort_on = 'created'
    show_searchform = False

    columns = (
        {'column': 'kind',
         'column_title': _(u'column_kind', default=u'Kind'),
         'transform': lambda item, value: item.activity.label,
         'sortable': False},

        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': resolve_notification_link,
         'sortable': False},

        {'column': 'actor_id',
         'column_title': _(u'column_Actor', default=u'Actor'),
         'transform': readable_actor,
         'sortable': False},

        {'column': 'created',
         'column_title': _(u'created', default=u'Created'),
         'transform': readable_date},
    )


@implementer(ITableSource)
@adapter(INotificationTableSourceConfig, Interface)
class NotificationTableSource(GeverTableSource):
    """Base table source adapter for notification listings, which get their
    data from the notification center.
    """

    def extend_query_with_ordering(self, query):
        if self.config.sort_on:
            query['sort_on'] = self.config.sort_on
            query['sort_reverse'] = self.config.sort_reverse

        return query

    def extend_query_with_textfilter(self, query, text):
        if text:
            if isinstance(text, str):
                text = text.decode('utf-8')

            query['filters'] = text.strip().split(' ')

        return query

    def extend_query_with_batching(self, query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        When `lazy` is set to `True` in the configuration, this method is
        not called.
        """
        if not self.config.batching_enabled:
            return query
        if not self.config.lazy:
            return query

        # we need to know how many records we would have without batching
        # TODO: set full length
        # self.full_length = query.count()
        pagesize = self.config.batching_pagesize
        current_page = self.config.batching_current_page
        start = pagesize * (current_page - 1)

        query['offset'] = start
        query['limit'] = pagesize

        return query

    def search_results(self, query):
        """Executes the query and returns a tuple of `results`.
        """
        return notification_center().list_notifications(**query)
