from ftw.builder import Builder
from ftw.builder import create
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

    def test_proposal_by_oguid_returns_proposal_with_oguid_param(self):
        proposal = create(Builder('proposal_model').having(
            admin_unit_id='unita', int_id=1))
        create(Builder('proposal_model').having(
            admin_unit_id='unita', int_id=2))
        create(Builder('proposal_model').having(
            admin_unit_id='unitb', int_id=1))

        self.assertEqual(proposal, Proposal.query.get_by_oguid(proposal.oguid))

    def test_proposal_by_oguid_returns_proposal_with_string_param(self):
        proposal = create(Builder('proposal_model').having(
            admin_unit_id='unita', int_id=1))
        create(Builder('proposal_model').having(
            admin_unit_id='unitb', int_id=2))
        create(Builder('proposal_model').having(
            admin_unit_id='unitb', int_id=1))

        self.assertEqual(proposal, Proposal.query.get_by_oguid('unita:1'))

    def test_get_by_oguid_returns_none_for_unknown_oguids(self):
        self.assertIsNone(Proposal.query.get_by_oguid('theanswer:42'))

    def test_by_admin_unit(self):
        proposal = create(Builder('proposal_model').having(
            admin_unit_id='unita', int_id=1))

        self.assertEqual(
            proposal,
            Proposal.query.by_admin_unit(MockAdminUnit('unita')).first())
