from datetime import datetime
from ftw.testing import MockTestCase
from opengever.core.testing import COMPONENT_UNIT_TESTING
from opengever.meeting.proposalhistory import BaseHistoryRecord
from opengever.meeting.proposalhistory import ProposalHistory
from opengever.testing import IntegrationTestCase
from persistent.mapping import PersistentMapping
from unittest import TestCase


class TestUnitPorposalHistory(MockTestCase):
    layer = COMPONENT_UNIT_TESTING

    def setUp(self):
        super(TestUnitPorposalHistory, self).setUp()
        self.history = ProposalHistory(context=None)

    def test_append_record_raises_when_timestamp_is_not_datetime(self):
        with self.assertRaises(TypeError):
            self.history.append_record(u'created', timestamp=object())

    def test_append_record_raises_when_name_is_not_registered(self):
        with self.assertRaises(ValueError):
            self.history.append_record(u'foo')

    def test_receive_record_raises_when_timestamp_is_not_datetime(self):
        with self.assertRaises(TypeError):
            self.history.receive_record(
                timestamp=object(), data=PersistentMapping())

    def test_receive_record_raises_when_data_is_not_pesistent_mapping(self):
        with self.assertRaises(TypeError):
            self.history.receive_record(
                timestamp=datetime.now(), data=PersistentMapping())


class TestBaseHistoryRecord(IntegrationTestCase):

    def test_registering_record_with_already_used_timestamp_raises_error(self):
        history = PersistentMapping()
        history[datetime(2010, 1, 1)] = object()
        record = BaseHistoryRecord(
            context=None, timestamp=datetime(2010, 1, 1))

        with self.assertRaises(ValueError):
            record.append_to(history)
