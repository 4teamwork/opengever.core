from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase


class TestCommitteeMemberVocabulary(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestCommitteeMemberVocabulary, self).setUp()

        self.admin_unit.public_url = 'http://nohost/plone'

        self.repo = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo))

        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .within(self.container)
                                .link_with(self.repository_folder))

        self.committee_model = self.committee.load_model()

        self.meeting = create(Builder('meeting').having(
            committee=self.committee_model))

        self.wrapper = MeetingWrapper(self.committee, self.meeting)

    def test_return_member_as_value(self):
        member = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))

        create(Builder('membership').having(
            committee=self.committee_model,
            member=member))

        vocabulary = get_committee_member_vocabulary(
            MeetingWrapper(self.committee, self.meeting))

        self.assertEqual(
            member,
            vocabulary._terms[0].value)

    def test_return_fullname_as_title(self):
        member = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))

        create(Builder('membership').having(
            committee=self.committee_model,
            member=member))

        vocabulary = get_committee_member_vocabulary(
            MeetingWrapper(self.committee, self.meeting))

        self.assertEqual(
            u'M\xfcller Hans',
            vocabulary._terms[0].title)

    def test_return_fullname_with_email_as_value(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'M\xfcller',
            email=u'mueller@example.com'))

        create(Builder('membership').having(
            committee=self.committee_model,
            member=member))

        vocabulary = get_committee_member_vocabulary(
            MeetingWrapper(self.committee, self.meeting))

        self.assertEqual(
            u'M\xfcller Hans (mueller@example.com)',
            vocabulary._terms[0].title)
