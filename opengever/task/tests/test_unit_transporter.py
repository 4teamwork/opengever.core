from datetime import date
from DateTime import DateTime
from datetime import datetime
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from z3c.relationfield import RelationValue
import json


class TestResponseTransporterSerialization(MockTestCase):

    def setUp(self):
        super(TestResponseTransporterSerialization, self).setUp()
        grok('opengever.task.transporter')

        task = self.providing_stub([ITask])
        self.replay()
        self.transporter = IResponseTransporter(task)
        self.transporter.intids_mapping = {}

    def assert_serialization(self, value):
        encoded = json.dumps(self.transporter._encode(value))
        self.assertEquals(value, self.transporter._decode(json.loads(encoded)))

    def test_string_encoding_decoding(self):
        self.assertEquals([u'string:utf8', u'hello'],
                          self.transporter._encode('hello'))
        self.assertEquals('hello',
                          self.transporter._decode([u'string:utf8', u'hello']))

    def test_unicode_encoding_decoding(self):
        self.assertEquals([u'unicode', u'hello'],
                          self.transporter._encode(u'hello'))
        self.assertEquals(u'hello',
                          self.transporter._decode([u'string:utf8', u'hello']))

    def test_handles_non_ascii_strings(self):
        self.assert_serialization('hell\xc3\xb6')

    def test_datetime_encoding_decoding(self):
        self.assert_serialization(datetime(2015, 11, 6, 13, 30))

    def test_list_encoding_decoding(self):
        self.assert_serialization(
            ['hell\xc3\xb6', u'hello', datetime(2015, 11, 6, 13, 30)])

    def test_dict_encoding_decoding(self):
        self.assert_serialization(
            {'key1': 'hell\xc3\xb6',
             'key2': u'hello',
             'key3': date(2015, 11, 6)})

    def test_relationvalue_encoding_decoding(self):
        self.transporter.intids_mapping = {111:222}
        value = RelationValue(111)
        self.assertEquals(
            RelationValue(222).to_id,
            self.transporter._decode(self.transporter._encode(value)).to_id)

    def test_encoder_raise_valueerror_when_intid_not_in_mapping(self):
        value = RelationValue(111)
        with self.assertRaises(ValueError):
            self.transporter._encode(value)

    def test_DateTime_encoding_decoding(self):
        self.assert_serialization(DateTime(2015, 11, 6, 13, 30))
