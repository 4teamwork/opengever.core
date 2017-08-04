from contextlib import nested
from opengever.testing import IntegrationTestCase


class TestWordAgendaItem(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    def test_deciding_meeting_item_does_not_create_an_excerpt(self):
        """When the word meeting feature is enabled, deciding a meeting item
        does not create and return a excerpt document automatically;
        this must now be done by hand.
        """
        self.login(self.administrator)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_word_proposal)

        with nested(self.observe_children(self.dossier),
                    self.observe_children(self.meeting_dossier)) as \
                    (dossier_children,
                     meeting_dossier_children):
            agenda_item.decide()

        self.assertEquals((), tuple(dossier_children['added']))
        self.assertEquals((), tuple(meeting_dossier_children['added']))
