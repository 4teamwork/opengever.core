from ftw.testbrowser import browsing
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.document.document import Document
from opengever.journal.handlers import DOCUMENT_ADDED_ACTION
from opengever.journal.handlers import DOCUMENT_MODIIFED_ACTION
from opengever.journal.handlers import DOCUMENT_STATE_CHANGED
from opengever.journal.handlers import PUBLIC_TRIAL_MODIFIED_ACTION
from opengever.journal.manager import JournalManager
from opengever.testing import IntegrationTestCase
from plone import api
from zope.i18n import translate


class TestDocumentEventJournalizations(IntegrationTestCase):

    def get_journal_entries(self, obj=None):
        if obj is None:
            obj = self.document
        return JournalManager(obj).list()

    def assert_journal_entry(self, action, title, entry):
        translated_title = translate(entry.get('action').get('title'),
                                     context=self.request)

        self.assertEqual(action, entry.get('action').get('type'))
        self.assertEqual(title, translated_title)

    @browsing
    def test_saving_edit_form_without_modifying_metadata_is_NOT_journalized(self, browser):
        self.login(self.regular_user, browser)
        journal_entries = self.get_journal_entries()

        browser.open(self.document, view='edit')
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(self.get_journal_entries(), journal_entries,
                         'Saving editform without modfifing metadata adds '
                         'wrongly a journal entry')

    @browsing
    def test_modifying_metadata_is_journalized(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='edit')
        browser.fill({'Description': 'Foo', 'Physical file': True})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entry)

    @browsing
    def test_modifying_the_file_is_NOT_journalized(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)
        journal_entries = self.get_journal_entries()

        browser.open(self.document, view='edit')
        browser.fill({'File': ('Raw file data', 'file.txt', 'text/plain'),
                      'form.widgets.file.action': 'replace'})
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(self.get_journal_entries(), journal_entries,
                         'Modifying only the file wrongly created a journal '
                         'entry')

    @browsing
    def test_modifying_the_file_and_metadata_is_journalized(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)

        browser.open(self.document, view='edit')
        browser.fill({'File': ('Raw file data', 'file.txt', 'text/plain'),
                      'form.widgets.file.action': 'replace',
                      'Description': 'Foo'})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entry)

    @browsing
    def test_modifying_the_public_trial_metadata_is_journalized(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='edit')
        browser.fill({'Disclosure status': PUBLIC_TRIAL_PRIVATE})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            PUBLIC_TRIAL_MODIFIED_ACTION,
            u'Disclosure status changed to "private".', entry)

    @browsing
    def test_modifying_the_public_trial_metadata_is_journalized_separately(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='edit')
        browser.fill({'Disclosure status': PUBLIC_TRIAL_PRIVATE,
                      'Description': 'Foo'})
        browser.css('#form-buttons-save').first.click()

        entries = self.get_journal_entries()

        self.assert_journal_entry(
            PUBLIC_TRIAL_MODIFIED_ACTION,
            u'Disclosure status changed to "private".', entries[-1])

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entries[-2])

    @browsing
    def test_modifying_the_public_trial_statement_is_journalized_as_a_metadata_change(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='edit')
        browser.fill({'Disclosure status statement': 'Fook'}).save()

        entries = self.get_journal_entries()

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entries[-1])

    def test_finalizing_the_document_is_journalized(self):
        self.login(self.regular_user)

        api.content.transition(obj=self.document,
                               transition=Document.finalize_transition)

        entries = self.get_journal_entries()

        self.assert_journal_entry(
            DOCUMENT_STATE_CHANGED, u'Document state changed: final', entries[-1])

    def test_reset_journal_after_creating_a_copy(self):
        self.login(self.regular_user)
        JournalManager(self.document).add_manual_entry('meeting', 'comment')

        cb = self.dossier.manage_copyObjects(self.document.getId())
        with self.observe_children(self.empty_dossier) as children:
            self.empty_dossier.manage_pasteObjects(cb)
        clone = children['added'].pop()

        journal = self.get_journal_entries()
        journal_clone = self.get_journal_entries(clone)

        self.assertNotEquals(len(journal), len(journal_clone))
        self.assertEquals(
            1,
            len(journal_clone),
            'Expect exactly one entry in the journal of the cloned document')

        self.assertEquals(DOCUMENT_ADDED_ACTION,
                          journal_clone[0]['action']['type'])
