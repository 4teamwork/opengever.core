from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.meeting.model.proposal import Proposal
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitProposal(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitProposal, self).setUp()
        self.session = self.layer.session

    def test_string_representation(self):
        proposal = create(Builder('proposal_model'))
        self.assertEqual('<Proposal 1234@foo>', str(proposal))
        self.assertEqual('<Proposal 1234@foo>', repr(proposal))

    def test_proposal_by_oguid_returns_proposal_with_oguid_param(self):
        create(Builder('proposal_model').having(
            int_id=2, admin_unit_id='unita'))
        proposal = create(Builder('proposal_model').having(
            int_id=1, admin_unit_id='unitb'))

        self.assertEqual(proposal, Proposal.query.get_by_oguid(proposal.oguid))

    def test_proposal_by_oguid_returns_proposal_with_string_param(self):
        proposal = create(Builder('proposal_model').having(
            int_id=1, admin_unit_id='unita'))
        create(Builder('proposal_model').having(
            int_id=2, admin_unit_id='unitb'))
        create(Builder('proposal_model').having(
            int_id=1, admin_unit_id='unitb'))

        self.assertEqual(proposal,
                         Proposal.query.get_by_oguid(Oguid('unita', 1)))

    def test_get_by_oguid_returns_none_for_unknown_oguids(self):
        self.assertIsNone(Proposal.query.get_by_oguid(Oguid('theanswer', 42)))

    def test_by_admin_unit(self):
        proposal = create(Builder('proposal_model').having(
            admin_unit_id='unita', int_id=1))

        self.assertEqual(
            proposal,
            Proposal.query.by_admin_unit(AdminUnit(unit_id='unita')).first())

    def test_active_query_returns_only_active_proposals(self):
        pending_proposal = create(Builder('proposal_model').having(
            int_id=1, workflow_state=Proposal.STATE_PENDING.name,
            ))
        submitted_proposal = create(Builder('proposal_model').having(
            int_id=2, workflow_state=Proposal.STATE_SUBMITTED.name,
            ))
        scheduled_proposal = create(Builder('proposal_model').having(
            int_id=3, workflow_state=Proposal.STATE_SCHEDULED.name,
            ))
        decided_proposal = create(Builder('proposal_model').having(
            int_id=4, workflow_state=Proposal.STATE_DECIDED.name,
            ))
        cancelled_proposal = create(Builder('proposal_model').having(
            int_id=5, workflow_state=Proposal.STATE_CANCELLED.name,
            ))

        self.assertItemsEqual(
            [pending_proposal, submitted_proposal, scheduled_proposal],
            Proposal.query.active().all())
