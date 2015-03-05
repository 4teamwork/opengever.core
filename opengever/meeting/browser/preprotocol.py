class PreProtocol(object):

    def __init__(self, agenda_item):
        self._agenda_item = agenda_item
        self._proposal = self._agenda_item.proposal

    @property
    def has_proposal(self):
        return self._proposal is not None

    @property
    def initial_position(self):
        return self._proposal.initial_position if self.has_proposal else None

    @property
    def considerations(self):
        return self._proposal.considerations if self.has_proposal else None

    @property
    def proposed_action(self):
        return self._proposal.proposed_action if self.has_proposal else None

    @property
    def discussion(self):
        return self._agenda_item.discussion

    @property
    def decision(self):
        return self._agenda_item.decision

    @property
    def name(self):
        return "preprotocols.{}".format(self._agenda_item.agenda_item_id)

    @property
    def title(self):
        return u"{} {}".format(self.number, self.description)

    @property
    def description(self):
        return self._agenda_item.get_title()

    @property
    def number(self):
        return self._agenda_item.number

    def update(self, request):
        """Update with changed data."""

        data = request.get(self.name)
        if not data:
            return

        if self.has_proposal:
            self._proposal.considerations = data.get('considerations')
            self._proposal.proposed_action = data.get('proposed_action')

        self._agenda_item.discussion = data.get('discussion')
        self._agenda_item.decision = data.get('decision')
