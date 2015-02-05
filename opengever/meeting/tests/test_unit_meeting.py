from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitMeeting(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMeeting, self).setUp()
        self.session = self.layer.session
        self.committee = create(Builder('committee_model'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            date=date(2010, 1, 1)))

    def test_string_representation(self):
        self.assertEqual('<Meeting at "2010-01-01">', str(self.meeting))
        self.assertEqual('<Meeting at "2010-01-01">', repr(self.meeting))

    def test_is_editable(self):
        self.assertTrue(self.meeting.is_editable())
        self.meeting.workflow_state = 'held'
        self.assertFalse(self.meeting.is_editable())

    def test_reorder_agenda_items(self):
        para = create(Builder('agenda_item')
                      .having(meeting=self.meeting, is_paragraph=True))
        item = create(Builder('agenda_item')
                      .having(meeting=self.meeting))

        self.meeting.reorder_agenda_items()
        self.assertEqual(1, para.sort_order)
        self.assertEqual(2, item.sort_order)
        self.assertIsNone(para.number)
        self.assertEqual('1.', item.number)

    def test_set_agenda_item_order(self):
        item_1 = create(Builder('agenda_item')
                        .having(meeting=self.meeting))
        item_2 = create(Builder('agenda_item')
                        .having(meeting=self.meeting))

        self.meeting.reorder_agenda_items(
            new_order=[item_2.agenda_item_id, item_1.agenda_item_id])

        self.assertSequenceEqual([item_2, item_1], self.meeting.agenda_items)
