import cgi

from ftw.table import helper
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import FilteredListingTab, SqlTableSource
from opengever.tabbedview.filters import Filter, FilterList
from opengever.tabbedview.helper import linked_ogds_author
from plone import api
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import Interface, implementer, implements


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


@implementer(ITableSource)
@adapter(IProposalTableSourceConfig, Interface)
class ProposalTableSource(SqlTableSource):

    searchable_columns = [Proposal.title]

    def search_results(self, query):
        """Filter proposals from sql query based on their catalog visibility."""
        results = super(ProposalTableSource, self).search_results(query)

        parent = self.config.context
        query = {
            'path': '/'.join(parent.getPhysicalPath()),
            'portal_type': 'opengever.meeting.proposal'
        }
        catalog = api.portal.get_tool('portal_catalog')
        visible_brains = catalog(query)

        visible_relative_paths = {
            '/'.join(brain.getPath().split('/')[2:]) for brain in visible_brains
        }

        return filter(
            lambda sql_proposal: sql_proposal.physical_path in visible_relative_paths,
            results
        )


def proposal_link(item, value):
    return item.get_link()


def translated_state(item, value):
    wrapper = u'<span class="wf-proposal-state-{0}">{1}</span>'
    return wrapper.format(
        item.get_state().title,
        translate(item.get_state().title, context=getRequest()))


def path_checkbox(item, value):
    title = cgi.escape(item.title, quote=True)
    return '''<input type="checkbox" class="noborder selectable"
    name="paths:list" id="%s" value="%s"
    alt="Select %s" title="Select %s" />''' % (
        item.id, item.getPath(), title, title)


class ActiveProposalFilter(Filter):
    """Only display active (from the dossiers side) Proposals."""

    def update_query(self, query):
        return query.active()


class DecidedProposalFilter(Filter):
    """Only display decided Proposals."""

    def update_query(self, query):
        return query.decided()


def get_description(item, value):
    """XSS safe description"""
    return item.get_description()


class ProposalListingTab(FilteredListingTab):
    implements(IProposalTableSourceConfig)

    filterlist_name = 'proposal_state_filter'
    filterlist = FilterList(
        Filter(
            'filter_proposals_all',
            _('all', default=u'All')),
        ActiveProposalFilter(
            'filter_proposals_active',
            _('active', default=u'Active'),
            default=True),
        DecidedProposalFilter(
            'filter_proposals_decided',
            _('decided', default=u'Decided'))
        )

    sort_on = ''
    show_selects = False

    @property
    def enabled_actions(self):
        actions = []
        if IDossierMarker.providedBy(self.context) and self.context.is_open():
            actions.append('move_proposal_items')

        return actions

    @property
    def columns(self):
        columns = []
        if self.enabled_actions:
            columns.append({'column': '',
                            'column_title': '',
                            'transform': path_checkbox,
                            'sortable': False,
                            'groupable': False,
                            'width': 30})
        columns.extend([
            {'column': 'decision_number',
             'column_title': _(u'label_decision_number',
                               default=u'Decision number'),
             'transform': lambda item, value: item.get_decision_number(),
             'sortable': False,
             'groupable': False,
             'width': 80},

            {'column': 'title',
             'column_title': _(u'column_title', default=u'Title'),
             'transform': proposal_link,
             'sortable': True,
             'groupable': False,
             'width': 180},

            {'column': 'description',
             'column_title': _(u'column_description', default=u'Description'),
             'transform': get_description,
             'sortable': True,
             'groupable': False,
             'width': 180},

            {'column': 'workflow_state',
             'column_title': _(u'column_state', default=u'State'),
             'transform': translated_state,
             'width': 120},

            {'column': 'committee_id',
             'column_title': _(u'column_comittee', default=u'Comittee'),
             'transform': lambda item, value: item.resolve_proposal().committee_name(),
             'width': 180},

            {'column': 'generated_meeting_link',
             'column_title': _(u'column_meeting', default=u'Meeting'),
             'transform': lambda item, value: item.get_meeting_link(),
             'sortable': False,
             'groupable': False,
             'width': 180},

            {'column': 'date_of_submission',
             'column_title': _(u'column_date_of_submission',
                               default=u'Date of submission'),
             'transform': helper.readable_date,
             'sortable': True,
             'groupable': True,
             'width': 120},

            {'column': 'issuer',
             'column_title': _(u'label_issuer',
                               default=u'Issuer'),
             'transform': linked_ogds_author,
             'sortable': True,
             'groupable': True,
             'width': 200},
        ])
        return columns

    def get_base_query(self):
        return Proposal.query.by_container(
            self.context, get_current_admin_unit())
