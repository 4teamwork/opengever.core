from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.model import Proposal
from opengever.meeting import _
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.base import BaseTableSource
from zope.interface import implements
from zope.interface import Interface


def proposal_link(item, value):
    return item.get_link()


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


class ProposalListingTab(BaseListingTab):
    implements(IProposalTableSourceConfig)

    model = Proposal

    columns = (
        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': proposal_link},

        # TODO: state translation, therefore the workflow has to moved to
        # the proposal model
        {'column': 'state',
         'column_title': _(u'column_state', default=u'State'),
         'transform': lambda item, value: item.workflow_state},

        {'column': 'comittee',
         'column_title': _(u'column_comittee', default=u'Comittee'),
         'transform': lambda item, value: item.committee.title},

        {'column': 'initial_position',
         'column_title': _(u'column_initial_position',
                           default=u'Initial Position')},

        {'column': 'proposed_action',
         'column_title': _(u'column_proposed_action',
                           default=u'Proposed action')},
    )


class ProposalTableSource(BaseTableSource):
    grok.implements(ITableSource)
    grok.adapts(ProposalListingTab, Interface)

    searchable_columns = [Proposal.title, Proposal.initial_position]
