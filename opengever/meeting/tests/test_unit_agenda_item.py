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
            committee=self.committee))

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
        self.assertEqual({'css_class': 'proposal',
                          'number': '1.',
                          'id': 1,
                          'title': u'Pr\xf6posal',
                          'has_proposal': True,
                          'link': u'<a href="http://example.com/public/meetings/proposal-1" title="Pr\xf6posal">Pr\xf6posal</a>'},
                         self.proposal_agenda_item.serialize())

    def test_decide_is_only_possible_if_agenda_item_is_pending(self):
        self.assertTrue(
            self.simple_agenda_item.is_decide_possible())

        self.simple_agenda_item.workflow_state = 'decided'
        self.assertFalse(
            self.simple_agenda_item.is_decide_possible())

    def test_decide_is_not_possible_for_paragraphs(self):
        item = create(Builder('agenda_item')
                      .having(is_paragraph=True, meeting=self.meeting))

        self.assertFalse(item.is_decide_possible())

    def test_is_decided_is_false_if_the_agendaitem_is_not_decided(self):
        agenda_item = create(Builder('agenda_item')
                             .having(title=u'Simple', meeting=self.meeting))

        self.assertFalse(agenda_item.is_decided())

    def test_is_decided_is_true_if_the_agendatiem_is_decided(self):
        agenda_item = create(Builder('agenda_item')
                             .having(title=u'Simple', meeting=self.meeting))

        agenda_item.workflow_state = 'decided'
        self.assertTrue(agenda_item.is_decided())

    def test_is_decided_is_false_for_paragraphs(self):
        agenda_item = create(Builder('agenda_item')
                             .having(is_paragraph=True, meeting=self.meeting))

        self.assertFalse(agenda_item.is_decided())

    def test_get_state(self):
        item = self.simple_agenda_item
        self.assertEquals(item.STATE_PENDING, item.get_state())

        item.workflow_state = 'decided'
        self.assertEquals(item.STATE_DECIDED, item.get_state())
