from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.journal.handlers import DOCUMENT_MODIIFED_ACTION
from opengever.journal.handlers import PUBLIC_TRIAL_MODIFIED_ACTION
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.annotation.interfaces import IAnnotations
from zope.i18n import translate


class TestDocumentEventJournalizations(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentEventJournalizations, self).setUp()

        self.document = create(Builder('document')
                               .titled(u'Testdocument')
                               .having(preserved_as_paper=True)
                               .checked_out_by(TEST_USER_ID)
                               .with_dummy_content())

    def get_journal_entries(self):
        annotations = IAnnotations(self.document)
        data = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        return data

    def assert_journal_entry(self, action, title, entry):
        translated_title = translate(entry.get('action').get('title'),
                                     context=self.document.REQUEST)

        self.assertEquals(action, entry.get('action').get('type'))
        self.assertEquals(title, translated_title)

    @browsing
    def test_saving_edit_form_without_modifying_metadata_is_NOT_journalized(self, browser):
        journal_entries = self.get_journal_entries()

        browser.login().open(self.document, view='edit')
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(self.get_journal_entries(), journal_entries,
                         'Saving editform without modfifing metadata adds '
                         'wrongly a journal entry')

    @browsing
    def test_modifying_metadata_is_journalized(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'Description': 'Foo', 'Preserved as paper': True})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entry)

    @browsing
    def test_modifying_the_file_is_journalized(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'File': ('Raw file data', 'file.txt', 'text/plain'),
                      'form.widgets.file.action': 'replace'})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed file', entry)

    @browsing
    def test_modifying_the_file_and_metadata_is_journalized(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'File': ('Raw file data', 'file.txt', 'text/plain'),
                      'form.widgets.file.action': 'replace',
                      'Description': 'Foo'})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed file and metadata', entry)

    @browsing
    def test_modifying_the_public_trial_metadata_is_journalized(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'Public Trial': PUBLIC_TRIAL_PRIVATE})
        browser.css('#form-buttons-save').first.click()

        entry = self.get_journal_entries()[-1]

        self.assert_journal_entry(
            PUBLIC_TRIAL_MODIFIED_ACTION,
            u'Public trial changed to "private".', entry)

    @browsing
    def test_modifying_the_public_trial_metadata_is_journalized_separately(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'Public Trial': PUBLIC_TRIAL_PRIVATE,
                      'Description': 'Foo'})
        browser.css('#form-buttons-save').first.click()

        entries = self.get_journal_entries()

        self.assert_journal_entry(
            PUBLIC_TRIAL_MODIFIED_ACTION,
            u'Public trial changed to "private".', entries[-1])

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entries[-2])

    @browsing
    def test_modifying_the_public_trial_statement_is_journalized_as_a_metadata_change(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'Public trial statement': 'Fook'}).save()

        entries = self.get_journal_entries()

        self.assert_journal_entry(
            DOCUMENT_MODIIFED_ACTION, u'Changed metadata', entries[-1])
