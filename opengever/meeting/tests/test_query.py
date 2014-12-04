from opengever.meeting.model.proposal import Proposal
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class MockAdminUnit(object):

    def __init__(self, unit_id):
        self.unit_id = unit_id

    def id(self):
        return self.unit_id


class TestProposalQuery(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestProposalQuery, self).setUp()
        self.session = self.layer.session

    def make_proposal(self, int_id, admin_unit_id):
        proposal = Proposal(int_id=int_id, admin_unit_id=admin_unit_id,
                            title=u'foo', physical_path='bar')
        self.session.add(proposal)
        return proposal

    def test_proposal_by_oguid_returns_proposal_with_oguid_param(self):
        proposal = self.make_proposal(1, 'unita')
        self.make_proposal(2, 'unita')
        self.make_proposal(1, 'unitb')

        self.assertEqual(proposal, Proposal.query.get_by_oguid(proposal.oguid))

    def test_proposal_by_oguid_returns_proposal_with_string_param(self):
        proposal = self.make_proposal(1, 'unita')
        self.make_proposal(2, 'unitb')
        self.make_proposal(1, 'unitb')

        self.assertEqual(proposal, Proposal.query.get_by_oguid('unita:1'))

    def test_get_by_oguid_returns_none_for_unknown_oguids(self):
        self.assertIsNone(Proposal.query.get_by_oguid('theanswer:42'))

    def test_by_admin_unit(self):
        proposal = create(Builder('proposal_model').having(
            admin_unit_id='unita', int_id=1))

        self.assertEqual(
            proposal,
            Proposal.query.by_admin_unit(MockAdminUnit('unita')).first())
