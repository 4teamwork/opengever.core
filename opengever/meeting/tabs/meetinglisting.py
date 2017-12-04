from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.base.browser.helper import get_css_class
from opengever.base.utils import escape_html
from opengever.meeting import _
from opengever.meeting.model import Meeting
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class IMeetingTableSourceConfig(ITableSourceConfig):
    """Marker interface for meeting table source configs."""


def translated_state(item, value):
    wrapper = u'<span class="{0}">{1}</span>'
    state = item.get_state()
    return wrapper.format(
        state.title,
        translate(state.title, context=getRequest()))


def dossier_link_or_title(item, value):
    dossier = item.get_dossier()
    if not dossier:
        return

    if not api.user.has_permission('View', obj=dossier):
        span = u'<span title="{0}" class="{1}">{0}</span>'.format(
            escape_html(safe_unicode(dossier.Title())),
            get_css_class(dossier))
        return span

    url = dossier.absolute_url()
    link = u'<a href="{0}" title="{1}" class="{2}">{1}</a>'.format(
        url,
        escape_html(safe_unicode(dossier.Title())),
        get_css_class(dossier))
    return link


class MeetingListingTab(BaseListingTab):
    implements(IMeetingTableSourceConfig)

    model = Meeting

    columns = (
        {'column': 'committee_id',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': lambda item, value: item.get_link(),
         'sortable': False,
         'groupable': False,
         'width': 300},

        {'column': 'workflow_state',
         'column_title': _(u'column_state', default=u'State'),
         'sortable': False,
         'groupable': False,
         'transform': translated_state},

        {'column': 'location',
         'column_title': _(u'column_location', default=u'Location')},

        {'column': 'start_datetime',
         'column_title': _(u'column_date', default=u'Date'),
         'transform': lambda item, value: item.get_date()},

        {'column': 'start_time',
         'column_title': _(u'column_from', default=u'From'),
         'transform': lambda item, value: item.get_start_time(),
         'sortable': False,
         'groupable': False},

        {'column': 'end_time',
         'column_title': _(u'column_to', default=u'To'),
         'transform': lambda item, value: item.get_end_time(),
         'sortable': False,
         'groupable': False},

        {'column': 'dossier',
         'column_title': _(u'dossier', default=u'Dossier'),
         'transform': dossier_link_or_title,
         'sortable': False,
         'groupable': False,
         'width': 300},
    )

    def get_base_query(self):
        return Meeting.query.filter_by(committee=self.context.load_model())


@implementer(ITableSource)
@adapter(IMeetingTableSourceConfig, Interface)
class MeetingTableSource(SqlTableSource):

    searchable_columns = [Meeting.location]
