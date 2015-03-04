from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface


def proposal_link(item, value):
    return item.get_link()


def translated_state(item, value):
    return translate(item.get_state().title, context=getRequest())


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


class ProposalListingTab(BaseListingTab):
    implements(IProposalTableSourceConfig)

    model = Proposal

    columns = (
        {'column': 'title',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': proposal_link},

        {'column': 'workflow_state',
         'column_title': _(u'column_state', default=u'State'),
         'transform': translated_state},

        {'column': 'committee_id',
         'column_title': _(u'column_comittee', default=u'Comittee'),
         'transform': lambda item, value: item.committee.title},

        {'column': 'initial_position',
         'column_title': _(u'column_initial_position',
                           default=u'Initial Position')},

        {'column': 'proposed_action',
         'column_title': _(u'column_proposed_action',
                           default=u'Proposed action')},
    )


class ProposalTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(ProposalListingTab, Interface)

    searchable_columns = [Proposal.title,
                          Proposal.initial_position,
                          Proposal.proposed_action]
