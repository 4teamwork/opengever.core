from opengever.base.viewlets.byline import BylineBase
from opengever.dossier import _
from opengever.ogds.base.actor import Actor
from opengever.ris.proposal import IProposal


class ProposalByline(BylineBase):
    def issuer(self):
        issuer = Actor.user(IProposal(self.context).issuer)
        return issuer.get_link()

    def get_items(self):
        items = super(ProposalByline, self).get_items()
        items.extend([
            {
                'class': 'responsible',
                'label': _(u'label_issuer', default='Issuer'),
                'content': self.issuer(),
                'replace': True
            },
            {
                'class': 'review_state',
                'label': _(u'label_workflow_state', default='State'),
                'content': self.workflow_state(),
                'replace': False
            }
        ])
        return items
