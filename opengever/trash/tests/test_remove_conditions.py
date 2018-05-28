from ftw.builder import Builder
from ftw.builder import create
from opengever.base.security import elevated_privileges
from opengever.testing import FunctionalTestCase
from opengever.trash.remover import RemoveConditionsChecker
from plone import api
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent


class TestRemoveConditionsChecker(FunctionalTestCase):

    def setUp(self):
        super(TestRemoveConditionsChecker, self).setUp()
        self.grant('Administrator')

    def assert_error_messages(self, expected, msgs):
        self.assertEquals(
            expected, [translate(msg) for msg in msgs])

    def test_document_must_not_have_relations(self):
        document_a = create(Builder('document'))
        document_b = create(Builder('document')
                            .trashed()
                            .relate_to([document_a]))

        checker = RemoveConditionsChecker(document_b)

        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document contains relations.'], checker.error_msg)

    def test_document_must_not_have_backreferences(self):
        document_a = create(Builder('document')
                            .trashed())
        document_b = create(Builder('document')
                            .titled('Doc b')
                            .relate_to([document_a]))

        notify(ObjectModifiedEvent(document_b))

        checker = RemoveConditionsChecker(document_a)

        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document is referred by the document(s) <a href=http://nohost/plone/document-2>Doc b</a>.'],
            checker.error_msg)

    def test_check_does_not_fail_if_document_has_no_longer_existent_backrefs(self):
        document_a = create(Builder('document')
                            .trashed())
        document_b = create(Builder('document')
                            .titled('Doc b')
                            .relate_to([document_a]))

        checker = RemoveConditionsChecker(document_a)
        self.assertFalse(checker.removal_allowed())

        with elevated_privileges():
            api.content.delete(obj=document_b)

        checker = RemoveConditionsChecker(document_a)
        self.assertTrue(checker.removal_allowed())

    def test_document_must_be_trashed(self):
        document = create(Builder('document'))
        checker = RemoveConditionsChecker(document)
        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document is not trashed.'],
            checker.error_msg)

    def test_document_must_not_already_be_removed(self):
        document = create(Builder('document')
                          .trashed()
                          .removed())
        checker = RemoveConditionsChecker(document)
        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document is already removed.'],
            checker.error_msg)

    def test_removal_allowed(self):
        document = create(Builder('document').trashed())
        checker = RemoveConditionsChecker(document)
        self.assertTrue(checker.removal_allowed())
