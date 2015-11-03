from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from opengever.testing.test_case import localized_datetime
from unittest2 import TestCase


class TestUnitAgendaItem(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitAgendaItem, self).setUp()
        self.session = self.layer.session

        self.committee = create(Builder('committee_model'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=localized_datetime(2010, 1, 1)))

        create(Builder('admin_unit').id('fd'))

        self.proposal = create(
            Builder('proposal_model').having(
                title=u'Pr\xf6posal',
                submitted_physical_path='meetings/proposal-1'))

        self.proposal.submitted_admin_unit_id = 'fd'
        self.proposal_agenda_item = create(
            Builder('agenda_item')
            .having(proposal=self.proposal,
                    meeting=self.meeting))
        self.simple_agenda_item = create(
            Builder('agenda_item')
            .having(title=u'Simple',
                    meeting=self.meeting))

    def test_test_title_is_proposal_title_when_proposal_is_available(self):
        self.assertEqual(
            self.proposal.title, self.proposal_agenda_item.get_title())

    def test_proposal_title_correctly_contains_number(self):
        self.assertEqual(
            u'1. Pr\xf6posal',
            self.proposal_agenda_item.get_title(include_number=True))

    def test_title_falls_back_to_agenda_item_title(self):
        self.assertEqual(u'Simple', self.simple_agenda_item.get_title())

    def test_agenda_item_title_correctly_contains_number(self):
        self.assertEqual(
            u'2. Simple',
            self.simple_agenda_item.get_title(include_number=True))

    def test_number_is_not_included_when_none(self):
        self.simple_agenda_item.number = None
        self.assertEqual(
            u'Simple', self.simple_agenda_item.get_title(include_number=True))

    def test_number_is_not_included_when_empty(self):
        self.simple_agenda_item.number = ''
        self.assertEqual(
            u'Simple', self.simple_agenda_item.get_title(include_number=True))

    def test_serialize(self):
        self.assertEqual({'css_class': '',
                          'number': '2.',
                          'id': 2,
                          'title': u'Simple',
                          'has_proposal': False,
                          'link': u'Simple',
                          },
                         self.simple_agenda_item.serialize())

    def test_serialize_proposal_agenda_item(self):
        self.assertEqual({'css_class': '',
                          'number': '1.',
                          'id': 1,
                          'title': u'Pr\xf6posal',
                          'has_proposal': True,
                          'link': u'<a href="http://example.com/public/meetings/proposal-1" title="Pr\xf6posal">Pr\xf6posal</a>'},
                         self.proposal_agenda_item.serialize())
