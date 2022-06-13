from DateTime import DateTime
from datetime import date
from datetime import datetime
from opengever.task.transporter import IResponseTransporter
from opengever.testing import IntegrationTestCase
from z3c.relationfield import RelationValue
import json


class TestResponseTransporterSerialization(IntegrationTestCase):

    def assert_serialization(self, value, transporter):
        encoded = json.dumps(transporter._encode(value))
        self.assertEquals(value, transporter._decode(json.loads(encoded)))

    def test_string_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assertEquals([u'string:utf8', u'hello'],
                          transporter._encode('hello'))
        self.assertEquals('hello',
                          transporter._decode([u'string:utf8', u'hello']))

    def test_unicode_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assertEquals([u'unicode', u'hello'],
                          transporter._encode(u'hello'))
        self.assertEquals(u'hello',
                          transporter._decode([u'string:utf8', u'hello']))

    def test_handles_non_ascii_strings(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assert_serialization('hell\xc3\xb6', transporter)

    def test_datetime_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assert_serialization(datetime(2015, 11, 6, 13, 30), transporter)

    def test_list_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assert_serialization(
            ['hell\xc3\xb6', u'hello', datetime(2015, 11, 6, 13, 30)], transporter)

    def test_dict_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assert_serialization(
            {'key1': 'hell\xc3\xb6',
             'key2': u'hello',
             'key3': date(2015, 11, 6)},
            transporter)

    def test_relationvalue_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        transporter.intids_mapping = {111:222}
        value = RelationValue(111)
        self.assertEquals(
            RelationValue(222).to_id,
            transporter._decode(transporter._encode(value)).to_id)

    def test_encoder_raise_valueerror_when_intid_not_in_mapping(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)
            transporter.intids_mapping = {}

        value = RelationValue(111)
        with self.assertRaises(ValueError):
            transporter._encode(value)

    def test_DateTime_encoding_decoding(self):
        with self.login(self.regular_user):
            transporter = IResponseTransporter(self.task)

        self.assert_serialization(DateTime(2015, 11, 6, 13, 30), transporter)
