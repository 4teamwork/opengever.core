from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitAgendaItem(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitAgendaItem, self).setUp()
        self.session = self.layer.session

        self.committee = create(Builder('committee_model'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=datetime(2010, 1, 1)))

        self.proposal = create(
            Builder('proposal_model')
            .having(title=u'Pr\xf6posal'))
        self.proposal_agenda_item = create(
            Builder('agenda_item')
            .having(proposal=self.proposal,
                    meeting=self.meeting,
                    number='2.'))
        self.simple_agenda_item = create(
            Builder('agenda_item')
            .having(title=u'Simple',
                    meeting=self.meeting,
                    number='3.'))

    def test_test_title_is_proposal_title_when_proposal_is_available(self):
        self.assertEqual(
            self.proposal.title, self.proposal_agenda_item.get_title())

    def test_proposal_title_correctly_contains_number(self):
        self.assertEqual(
            u'2. Pr\xf6posal',
            self.proposal_agenda_item.get_title(include_number=True))

    def test_title_falls_back_to_agenda_item_title(self):
        self.assertEqual(u'Simple', self.simple_agenda_item.get_title())

    def test_agenda_item_title_correctly_contains_number(self):
        self.assertEqual(
            u'3. Simple',
            self.simple_agenda_item.get_title(include_number=True))

    def test_number_is_not_included_when_none(self):
        self.simple_agenda_item.number = None
        self.assertEqual(
            u'Simple', self.simple_agenda_item.get_title(include_number=True))

    def test_number_is_not_included_when_empty(self):
        self.simple_agenda_item.number = ''
        self.assertEqual(
            u'Simple', self.simple_agenda_item.get_title(include_number=True))
