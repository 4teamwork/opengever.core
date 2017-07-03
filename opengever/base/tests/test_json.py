from datetime import datetime
from opengever.base.jsondecoder import AdvancedJSONDecoder
from opengever.base.jsonencoder import AdvancedJSONEncoder
from unittest import TestCase
from uuid import UUID
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

    def test_serializes_uuid(self):
        uuid = UUID('61df790e-e547-416f-b661-d236a13250de')
        encoder = AdvancedJSONEncoder()
        self.assertEquals('["61df790e-e547-416f-b661-d236a13250de"]',
                          encoder.encode([uuid]))


class TestAdvancedJSONDecoder(TestCase):

    def test_deserializes_naive_datetime(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode('{"dt": "2014-12-31T15:45:30.000999"}')
        self.assertEquals(
            {'dt': datetime(2014, 12, 31, 15, 45, 30, 999)},
            obj)

    def test_deserializes_aware_datetime(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode('{"dt": "2014-12-31T15:45:30.000999+00:00"}')
        self.assertEquals(
            {'dt': datetime(2014, 12, 31, 15, 45, 30, 999, tzinfo=pytz.UTC)},
            obj)

    def test_returns_deserialized_aware_datetimes_as_utc(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode('{"dt": "2010-01-01T12:00:00+01:00"}')
        self.assertEquals(
            {'dt': datetime(2010, 1, 1, 11, 0, tzinfo=pytz.UTC)},
            obj)
