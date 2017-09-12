from ftw.upgrade import UpgradeStep


class FixSharedExcerptListReference(UpgradeStep):
    """Fix shared excerpt list reference.

    Excerpts are stored in the meeting-dossier. We fix shared excerpt lists by
    creating a new list instance and filtering out the excerpts that come from
    foreign meeting dossiers should they be present in the excerpt list.

    We can't completely fix relations within the same meeting, so it may happen
    that multiple submitted proposals point to the same excerpt within the same
    meeting dossier.
    """
    def __call__(self):
        msg = 'Fix shared excerpt list reference.'
        query = {'portal_type': 'opengever.meeting.submittedproposal'}

        for submitted_proposal in self.objects(query, msg):
            self._fix_excerpts_relation(submitted_proposal)

    def _fix_excerpts_relation(self, submitted_proposal):
        # getattr will/should always return the default value from the
        # ISubmittedProposal schema, but to be extra certain that we don't
        # cause unexpected errors we add this safeguard here
        excerpt_relations = getattr(submitted_proposal, 'excerpts', None)
        if not excerpt_relations:
            # empty lists will be correctly intialized/replaced with a new
            # instance when the first excerpt is created, we don't need to
            # set the attribute in that case
            return

        meeting_dossier = self._get_meeting_dossier(submitted_proposal)
        valid_excerpts = set(meeting_dossier.listFolderContents())
        valid_relations = []

        for relation_value in excerpt_relations:
            excerpt_document = relation_value.to_object
            if excerpt_document in valid_excerpts:
                valid_relations.append(relation_value)

        submitted_proposal.excerpts = valid_relations

    def _get_meeting_dossier(self, submitted_proposal):
        proposal_model = submitted_proposal.load_model()
        if not proposal_model.agenda_item:
            return None

        return proposal_model.agenda_item.meeting.get_dossier()
