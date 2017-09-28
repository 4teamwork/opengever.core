from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.service import meeting_service
from opengever.testing import MEMORY_DB_LAYER
from unittest import TestCase


class TestService(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestService, self).setUp()
        self.session = self.layer.session
        self.service = meeting_service()

    def test_all_committees(self):
        committee1 = create(Builder('committee_model'))
        committee2 = create(Builder('committee_model').having(int_id=5678))
        self.assertEqual([committee1, committee2],
                         self.service.all_committees())

    def test_fetch_committee_returns_correct_committee(self):
        create(Builder('committee_model'))
        committee2 = create(Builder('committee_model').having(int_id=5678))

        self.assertEqual(
            committee2,
            self.service.fetch_committee(committee2.committee_id))

    def test_fetch_committee_returns_none_for_invalid_id(self):
        self.assertIsNone(self.service.fetch_committee(1337))
