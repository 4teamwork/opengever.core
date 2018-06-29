from opengever.meeting.model import Committee
from opengever.meeting.vocabulary import ActiveCommitteeVocabulary
from opengever.meeting.vocabulary import CommitteeVocabulary
from opengever.testing import IntegrationTestCase


class TestCommitteeVocabulary(IntegrationTestCase):

    def test_get_committees_returns_list_sorted_by_title(self):
        for simple_vocabulary in (CommitteeVocabulary(), ActiveCommitteeVocabulary(), ):
            titles_from_vocabulary = [term.title for term in simple_vocabulary(context=None)]
            unsorted_titles = [committee.title for committee in Committee.query.all()]
            sorted_titles = [u'Kommission f\xfcr Verkehr', u'Rechnungspr\xfcfungskommission']

            self.assertNotEquals(unsorted_titles, titles_from_vocabulary)
            self.assertEquals(sorted_titles, titles_from_vocabulary)
