from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import Meeting
from opengever.testing import MEMORY_DB_LAYER
from unittest import TestCase
import pytz


class TestUnitMeeting(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMeeting, self).setUp()
        self.session = self.layer.session
        self.committee = create(Builder('committee_model'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=pytz.UTC.localize(datetime(2010, 1, 1, 10, 30))))

    def test_string_representation(self):
        self.assertEqual(
            '<Meeting at "2010-01-01 10:30:00+00:00">', str(self.meeting))
        self.assertEqual(
            '<Meeting at "2010-01-01 10:30:00+00:00">', repr(self.meeting))

    def test_has_protocol_document(self):
        self.assertFalse(self.meeting.has_protocol_document())
        self.meeting.protocol_document = GeneratedProtocol(
            admin_unit_id='foo', int_id=1, generated_version=42)
        self.assertTrue(self.meeting.has_protocol_document())

    def test_meeting_title(self):
        self.assertEqual(
            u'My Title',
            Meeting(title="My Title").get_title())

    def test_reorder_agenda_items(self):
        para = create(Builder('agenda_item')
                      .having(meeting=self.meeting, is_paragraph=True))
        item = create(Builder('agenda_item')
                      .having(meeting=self.meeting))

        self.meeting.reorder_agenda_items()
        self.assertEqual(1, para.sort_order)
        self.assertEqual(2, item.sort_order)
        self.assertIsNone(para.item_number)
        self.assertEqual(1, item.item_number)

    def test_set_agenda_item_order(self):
        item_1 = create(Builder('agenda_item')
                        .having(meeting=self.meeting))
        item_2 = create(Builder('agenda_item')
                        .having(meeting=self.meeting))

        self.meeting.reorder_agenda_items(
            new_order=[item_2.agenda_item_id, item_1.agenda_item_id])

        self.assertSequenceEqual([item_2, item_1], self.meeting.agenda_items)
        self.assertEqual(1, item_2.sort_order)
        self.assertEqual(2, item_1.sort_order)
