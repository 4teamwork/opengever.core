from datetime import datetime
from opengever.base.advancedjson import AdvancedJSONDecoder
from opengever.base.advancedjson import AdvancedJSONEncoder
from opengever.base.advancedjson import CannotDecodeJsonType
from persistent.mapping import PersistentMapping
from unittest import TestCase
from uuid import UUID
from uuid import uuid4
import pytz


class TestRoundtrip(TestCase):

    maxDiff = None

    def test_encoder_decoder_roundtrip(self):
        encoder = AdvancedJSONEncoder()
        decoder = AdvancedJSONDecoder()

        input = {
            u'dt_naive': datetime(2014, 12, 31, 15, 45, 30, 999),
            u'dt_aware': datetime(2099, 1, 3, 15, 45, 30, 12, tzinfo=pytz.UTC),
            u'somethingelse': u'2017-1-1',
            u'justanumber': 49184913,
            u'dict': dict(qux=u'blabla'),
            u'list': [1, 2, u'44'],
            u'uuid': uuid4(),
            u'set': set([1, 2, u'gugus']),
            u'pmapping': PersistentMapping({u'qux': 123, u'meh': u'bar'}),
        }
        output = decoder.decode(encoder.encode(input))
        self.assertEquals(input, output)


class TestAdvancedJSONEncoder(TestCase):

    def test_serializes_naive_datetime(self):
        encoder = AdvancedJSONEncoder()
        dt = datetime(2014, 12, 31, 15, 45, 30, 999)

        self.assertEquals(
            '[{'
            '"_advancedjson_value": "2014-12-31T15:45:30.000999", '
            '"_advancedjson_type": "datetime"'
            '}]',
            encoder.encode([dt]))

    def test_serializes_aware_datetime(self):
        encoder = AdvancedJSONEncoder()
        dt = datetime(2014, 12, 31, 15, 45, 30, 999, tzinfo=pytz.UTC)

        self.assertEquals(
            '[{'
            '"_advancedjson_value": "2014-12-31T15:45:30.000999+00:00", '
            '"_advancedjson_type": "datetime"'
            '}]',
            encoder.encode([dt]))

    def test_delegates_unknown_objects_to_default_encoder(self):
        encoder = AdvancedJSONEncoder()
        data = [object()]
        with self.assertRaises(TypeError):
            encoder.encode(data)

    def test_serializes_set(self):
        encoder = AdvancedJSONEncoder()
        data = set(['foo'])

        self.assertEquals(
            '[{'
            '"_advancedjson_value": ["foo"], '
            '"_advancedjson_type": "set"'
            '}]',
            encoder.encode([data]))

    def test_serializes_uuid(self):
        uuid = UUID('61df790e-e547-416f-b661-d236a13250de')
        encoder = AdvancedJSONEncoder()

        self.assertEquals(
            '[{'
            '"_advancedjson_value": "61df790e-e547-416f-b661-d236a13250de", '
            '"_advancedjson_type": "UUID"'
            '}]',
            encoder.encode([uuid]))

    def test_serializes_persistent_mapping_as_dict(self):
        data = PersistentMapping(foo='bar')
        encoder = AdvancedJSONEncoder()

        self.assertEquals(
            '[{'
            '"_advancedjson_value": {"foo": "bar"}, '
            '"_advancedjson_type": "PersistentMapping"'
            '}]',
            encoder.encode([data]))


class TestAdvancedJSONDecoder(TestCase):

    def test_deserializes_naive_datetime(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode(
            '[{'
            '"_advancedjson_value": "2014-12-31T15:45:30.000999", '
            '"_advancedjson_type": "datetime"'
            '}]')
        self.assertEquals(
            [datetime(2014, 12, 31, 15, 45, 30, 999)], obj)

    def test_deserializes_aware_datetime(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode(
            '[{'
            '"_advancedjson_value": "2014-12-31T15:45:30.000999+00:00", '
            '"_advancedjson_type": "datetime"'
            '}]')
        self.assertEquals(
            [datetime(2014, 12, 31, 15, 45, 30, 999, tzinfo=pytz.UTC)], obj)

    def test_returns_deserialized_aware_datetimes_as_utc(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode(
            '[{'
            '"_advancedjson_value": "2010-01-01T12:00:00+01:00", '
            '"_advancedjson_type": "datetime"'
            '}]')
        self.assertEquals(
            [datetime(2010, 1, 1, 11, 0, tzinfo=pytz.UTC)], obj)

    def test_deserializes_set(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode(
            '[{'
            '"_advancedjson_value": ["foo"], '
            '"_advancedjson_type": "set"'
            '}]')
        self.assertEquals(
            [set(['foo'])], obj)

    def test_deserializes_uuid(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode(
            '[{'
            '"_advancedjson_value": "61df790e-e547-416f-b661-d236a13250de", '
            '"_advancedjson_type": "UUID"'
            '}]')
        self.assertEquals(
            [UUID('61df790e-e547-416f-b661-d236a13250de')], obj)

    def test_deserializes_persistent_mapping(self):
        decoder = AdvancedJSONDecoder()
        obj = decoder.decode(
            '[{'
            '"_advancedjson_value": {"foo": "bar"}, '
            '"_advancedjson_type": "PersistentMapping"'
            '}]')
        self.assertEquals(
            [PersistentMapping(foo='bar')], obj)

    def test_raises_in_attempt_to_decode_unknown_object(self):
        with self.assertRaises(CannotDecodeJsonType):
            decoder = AdvancedJSONDecoder()
            decoder.decode(
                '[{'
                '"_advancedjson_value": "does not matter",'
                '"_advancedjson_type": "type that does not exist"'
                '}]')
