from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.security import elevated_privileges
from opengever.testing import IntegrationTestCase
from opengever.trash.remover import RemoveConditionsChecker
from opengever.trash.remover import Remover
from plone import api
from zope.i18n import translate


class TestRemoveConditionsChecker(IntegrationTestCase):

    def assert_error_messages(self, expected, msgs):
        self.assertEquals(
            expected, [translate(msg) for msg in msgs])

    def test_document_must_not_have_relations(self):
        self.login(self.manager)

        document_b = create(Builder('document')
                            .relate_to([self.document])
                            .trashed())

        checker = RemoveConditionsChecker(document_b)

        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document contains relations.'], checker.error_msg)

    @browsing
    def test_document_must_not_have_backreferences(self, browser):
        self.login(self.manager, browser=browser)
        self.trash_documents(self.subdocument)

        browser.open(self.taskdocument, view='edit')
        browser.fill({'Related Documents': [self.subdocument]})
        browser.find('Save').click()

        checker = RemoveConditionsChecker(self.subdocument)

        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document is referred by the document(s) <a href={}>{}</a>.'.format(
                self.taskdocument.absolute_url(), self.taskdocument.title)],
            checker.error_msg)

    @browsing
    def test_check_does_not_fail_if_document_has_no_longer_existent_backrefs(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.taskdocument, view='edit')
        browser.fill({'Related Documents': [self.subdocument]})
        browser.find('Save').click()

        self.trash_documents(self.subdocument)

        checker = RemoveConditionsChecker(self.subdocument)
        self.assertFalse(checker.removal_allowed())

        with elevated_privileges():
            api.content.delete(obj=self.taskdocument)

        checker = RemoveConditionsChecker(self.subdocument)
        self.assertTrue(checker.removal_allowed())

    def test_document_must_be_trashed(self):
        self.login(self.manager)

        checker = RemoveConditionsChecker(self.empty_document)
        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document is not trashed.'], checker.error_msg)

    def test_document_must_not_already_be_removed(self):
        self.login(self.manager)

        self.trash_documents(self.empty_document)
        Remover([self.empty_document]).remove()

        checker = RemoveConditionsChecker(self.empty_document)
        self.assertFalse(checker.removal_allowed())
        self.assert_error_messages(
            [u'The document is already removed.'],
            checker.error_msg)

    def test_removal_allowed(self):
        self.login(self.manager)
        self.trash_documents(self.empty_document)

        checker = RemoveConditionsChecker(self.empty_document)
        self.assertTrue(checker.removal_allowed())
