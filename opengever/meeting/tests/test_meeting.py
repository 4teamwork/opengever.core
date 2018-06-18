from opengever.meeting.vocabulary import get_committee_member_vocabulary
from opengever.testing import IntegrationTestCase


class TestCommitteeMemberVocabulary(IntegrationTestCase):

    def test_return_fullname_with_email_as_title(self):
        self.login(self.meeting_user)
        vocabulary = get_committee_member_vocabulary(self.meeting)

        self.assertEqual(
            [u'Sch\xf6ller Heidrun (h.schoeller@web.de)',
             u'W\xf6lfl Gerda (g.woelfl@hotmail.com)',
             u'Wendler Jens (jens-wendler@gmail.com)'],
            [term.title for term in vocabulary])

    def test_returns_member_as_value(self):
        self.login(self.meeting_user)
        vocabulary = get_committee_member_vocabulary(self.meeting)

        self.assertEqual(
            [self.committee_president.model,
             self.committee_participant_1.model,
             self.committee_participant_2.model],
            [term.value for term in vocabulary])

    def test_omits_braces_when_no_email_is_available(self):
        self.login(self.meeting_user)
        self.committee_president.model.email = None

        vocabulary = get_committee_member_vocabulary(self.meeting)
        self.assertEqual(u'Sch\xf6ller Heidrun', vocabulary._terms[0].title)
