from opengever.globalindex.oguid import Oguid
from opengever.meeting.model.proposal import Proposal as ProposalModel
from plone.dexterity.content import Container
from plone.directives import form
from zope.interface import implements


class IProposal(form.Schema):
    """Proposal Schema Interface"""


class Proposal(Container):
    implements(IProposal)

    def load_model(self):
        return ProposalModel.query.by_oguid(Oguid.for_object(self))

    def get_searchable_text(self):
        model = self.load_model()
        if not model:
            return ''

        return model.get_searchable_text()
