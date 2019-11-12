from opengever.base.docprops import BaseDocPropertyProvider
from opengever.meeting.proposal import IBaseProposal
from zope.component import adapter
from zope.i18n import translate


@adapter(IBaseProposal)
class ProposalDocPropertyProvider(BaseDocPropertyProvider):

    DEFAULT_PREFIX = ('meeting',)

    def _collect_properties(self):
        properties = {
            'decision_number': '',
            'agenda_item_number': '',
            'agenda_item_number_raw': '',
            'proposal_title': self.context.title,
            'proposal_description': self.context.description,
            'proposal_state': translate(self.context.get_state().title,
                                        context=self.context.REQUEST),
        }

        model = self.context.load_model()
        if not model:
            return properties

        agenda_item = model.agenda_item
        if not agenda_item:
            return properties

        properties['decision_number'] = agenda_item.get_decision_number() or ''
        properties['agenda_item_number'] = agenda_item.formatted_number
        properties['agenda_item_number_raw'] = agenda_item.item_number
        return properties
