from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.trash.remover import RemoveConditions
from plone.app.testing import TEST_USER_ID
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent


class TestRemoveConditions(FunctionalTestCase):

    def setUp(self):
        super(TestRemoveConditions, self).setUp()
        self.grant('Administrator')

    def assert_error_messages(self, expected, msgs):
        self.assertEquals(
            expected, [translate(msg) for msg in msgs])

    def test_document_has_to_be_checked_in(self):
        document = create(Builder('document')
                          .trashed()
                          .checked_out_by(TEST_USER_ID))
        checker = RemoveConditions(document)

        self.assertFalse(checker.remove_allowed())
        self.assert_error_messages(
            [u'The document is still checked out.'], checker.error_msg)

    def test_document_has_no_relations(self):
        document_a = create(Builder('document'))
        document_b = create(Builder('document')
                            .trashed()
                            .relate_to([document_a]))

        checker = RemoveConditions(document_b)

        self.assertFalse(checker.remove_allowed())
        self.assert_error_messages(
            [u'The document contains relations.'], checker.error_msg)

    def test_document_has_no_backreferences(self):
        document_a = create(Builder('document')
                            .trashed())
        document_b = create(Builder('document')
                            .titled('Doc b')
                            .relate_to([document_a]))

        notify(ObjectModifiedEvent(document_b))

        checker = RemoveConditions(document_a)

        self.assertFalse(checker.remove_allowed())
        self.assert_error_messages(
            [u'The document is reffered by the document <a href=http://nohost/plone/document-2>Doc b</a>.'],
            checker.error_msg)

    def test_document_is_trashed(self):
        document = create(Builder('document'))
        checker = RemoveConditions(document)
        self.assertFalse(checker.remove_allowed())
        self.assert_error_messages(
            [u'The documents is not trashed.'],
            checker.error_msg)

    def test_remove_allowed(self):
        document = create(Builder('document').trashed())
        checker = RemoveConditions(document)
        self.assertTrue(checker.remove_allowed())
