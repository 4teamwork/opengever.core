from ftw.upgrade import UpgradeStep
from opengever.meeting.model import SubmittedDocument
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import logging

logger = logging.getLogger('opengever.core')


class FixMissingRelatedProposalDocuments(UpgradeStep):
    """Fix missing related proposal documents.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        updated_proposals = []
        updated_documents = 0

        submitted_documents = SubmittedDocument.query.all()

        # The postgres db still contains all the relations between documents and
        # proposals. We iterate over each submitted document relation in the
        # postgres db and look if the proposal have the document in the related
        # items. If not, we add it.
        #
        # Submitted proposals are not affected by this issue.
        for submitted_document in submitted_documents:
            proposal = submitted_document.proposal.resolve_proposal()
            source_document = submitted_document.resolve_source()

            if source_document not in self.lookup_relations(proposal):
                proposal.relatedItems.append(self.get_intid(source_document))
                proposal._p_changed = 1

                # For loggin
                updated_documents += 1
                if proposal not in updated_proposals:
                    updated_proposals.append(proposal)

        logger.info(
            "Fixed {} proposals by adding {} missing document relations".format(
                len(updated_proposals), updated_documents))

    def lookup_relations(self, obj):
        return [rel.to_object for rel in obj.relatedItems]

    def get_intid(self, obj):
        return RelationValue(getUtility(IIntIds).getId(obj))
