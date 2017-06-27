from datetime import datetime
from opengever.base.jsonencoder import AdvancedJSONEncoder
from unittest import TestCase
import pytz


class TestAdvancedJSONEncoder(TestCase):

    def test_serializes_naive_datetime(self):
        encoder = AdvancedJSONEncoder()
        dt = datetime(2014, 12, 31, 15, 45, 30, 999)
        self.assertEquals('["2014-12-31T15:45:30.000999"]',
                          encoder.encode([dt]))

    def test_serializes_aware_datetime(self):
        encoder = AdvancedJSONEncoder()
        dt = datetime(2014, 12, 31, 15, 45, 30, 999, tzinfo=pytz.UTC)
        self.assertEquals('["2014-12-31T15:45:30.000999+00:00"]',
                          encoder.encode([dt]))

    def test_delegates_unknown_objects_to_default_encoder(self):
        encoder = AdvancedJSONEncoder()
        data = [object()]
        with self.assertRaises(TypeError):
            encoder.encode(data)

    def test_serializes_set(self):
        encoder = AdvancedJSONEncoder()
        data = set(['foo'])
        self.assertEquals('[["foo"]]',
                          encoder.encode([data]))
