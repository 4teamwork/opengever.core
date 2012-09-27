from DateTime import DateTime
from datetime import datetime
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from persistent.list import PersistentList
from z3c.relationfield import RelationValue
import json


class TestResponseTransporter(MockTestCase):

    def setUp(self):
        grok('opengever.task.transporter')

    def _compare(self, a, b, mapping):
        if isinstance(a, RelationValue):
            self.assertEquals(mapping.get(a.to_id), b.to_id)
        else:
            self.assertEquals(a, b)

    def test_encode(self):

        values = [
            'hello'
            'hell\xc3\xb6',
            u'helllo',
            datetime(2012, 1, 1),
            DateTime(2012, 1, 1),
            RelationValue(1111),
            ['hello', u'hello', 'hell\xc3\xb6'],
            PersistentList(['hello', u'hello']),
            [RelationValue(1111), RelationValue(3333), RelationValue(5555)]
            ]

        task = self.providing_stub([ITask])

        self.replay()

        transporter = IResponseTransporter(task)
        transporter.intids_mapping = {1111: 2222, 3333: 5555, 5555: 3333}

        for value in values:
            encoded_value = json.dumps(transporter._encode(value))
            decoded_value = transporter._decode(json.loads(encoded_value))

            # compare the value with the de- and encoded value
            if isinstance(value, list):
                for i in range(len(value)):
                    self._compare(
                        value[i], decoded_value[i], transporter.intids_mapping)
            else:
                self._compare(value, decoded_value, transporter.intids_mapping)
