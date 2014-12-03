from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.service import meeting_service
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestService(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestService, self).setUp()
        self.session = self.layer.session
        self.service = meeting_service()

    def test_all_commissions(self):
        commission1 = create(Builder('commission'))
        commission2 = create(Builder('commission'))
        self.assertEqual([commission1, commission2],
                         self.service.all_commissions())

    def test_fetch_commission_returns_correct_commission(self):
        create(Builder('commission'))
        commission2 = create(Builder('commission'))

        self.assertEqual(
            commission2,
            self.service.fetch_commission(commission2.commission_id))

    def test_fetch_commission_returns_none_for_invalid_id(self):
        self.assertIsNone(self.service.fetch_commission(1337))
