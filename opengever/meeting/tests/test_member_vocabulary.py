from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestMemberVocabulary(FunctionalTestCase):

    def test_member_vocabulary_sorts_by_fullname(self):
        member1 = create(Builder('member')
                         .having(firstname=u'Xxx', lastname=u'Peter'))
        member2 = create(Builder('member')
                         .having(firstname=u'Aaa', lastname=u'Peter'))

        vocfactory = getUtility(IVocabularyFactory,
                                name=u'opengever.meeting.MemberVocabulary')

        vocabulary = vocfactory(context=None)
        self.assertEqual([member2.fullname, member1.fullname],
                         [each.title for each in vocabulary])
