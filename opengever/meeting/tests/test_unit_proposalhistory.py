from datetime import datetime
from opengever.meeting.proposalhistory import ProposalHistory
from persistent.mapping import PersistentMapping
from unittest2 import TestCase


class TestUnitPorposalHistory(TestCase):

    def setUp(self):
        self.history = ProposalHistory(context=None)

    def test_append_record_raises_when_timestamp_is_not_datetime(self):
        with self.assertRaises(TypeError):
            self.history.append_record('created', timestamp=object())

    def test_append_record_raises_when_name_is_not_registered(self):
        with self.assertRaises(ValueError):
            self.history.append_record('foo')

    def test_receive_record_raises_when_timestamp_is_not_datetime(self):
        with self.assertRaises(TypeError):
            self.history.receive_record(
                timestamp=object(), data=PersistentMapping())

    def test_receive_record_raises_when_data_is_not_pesistent_mapping(self):
        with self.assertRaises(TypeError):
            self.history.receive_record(
                timestamp=datetime.now(), data=PersistentMapping())
