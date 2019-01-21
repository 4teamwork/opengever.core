from AccessControl import Unauthorized
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from opengever.document.document import Document
from opengever.journal.handlers import OBJECT_REMOVED
from opengever.journal.handlers import OBJECT_RESTORED
from opengever.mail.mail import OGMail
from opengever.testing import IntegrationTestCase
from opengever.trash.remover import Remover
from plone import api


class TestRemover(IntegrationTestCase):
    def test_changes_state_to_removed_for_all_documents(self):
        self.login(self.manager)

        documents = [self.inbox_document, self.empty_document]
        self.trash_documents(*documents)

        Remover(documents).remove()
        self.assertEqual(Document.removed_state, api.content.get_state(obj=self.empty_document))
        self.assertEqual(Document.removed_state, api.content.get_state(obj=self.inbox_document))

    def test_raises_runtimeerror_when_preconditions_are_not_satisified(self):
        self.login(self.manager)

        self.trash_documents(self.inbox_document)

        with self.assertRaises(RuntimeError) as cm:
            Remover([self.document, self.inbox_document]).remove()

        self.assertEqual('RemoveConditions not satisified', str(cm.exception))

    def test_raises_unauthorized_when_user_does_not_have_remove_permission(self):
        self.login(self.regular_user)

        self.trash_documents(self.empty_document)

        with self.assertRaises(Unauthorized):
            Remover([self.empty_document]).remove()


class TestRemoveConfirmationView(IntegrationTestCase):

    @browsing
    def test_redirects_to_trash_tab_when_no_documents_selected(self, browser):
        self.login(self.manager, browser)
        browser.open(self.dossier, view='remove_confirmation')

        self.assertEqual('{}#trash'.format(self.dossier.absolute_url()), browser.url)
        assert_message('You have not selected any items.')

    @browsing
    def test_submit_button_is_disabled_when_preconditions_are_not_satisfied(self, browser):
        self.login(self.manager, browser)

        browser.open(self.dossier, self.make_path_param(self.document, self.empty_document), view='remove_confirmation')

        self.assertEqual('disabled', browser.css('#form-buttons-delete').first.get('disabled'))

    @browsing
    def test_shows_error_message_on_top(self, browser):
        self.login(self.manager, browser)

        browser.open(self.dossier, self.make_path_param(self.document, self.empty_document), view='remove_confirmation')

        self.assertEqual(
            ["Error The selected documents can't be removed, see error messages below."], browser.css('.message').text)

    @browsing
    def test_shows_specific_message_on_documents_error_box(self, browser):
        self.login(self.manager, browser)

        browser.open(self.dossier, self.make_path_param(self.empty_document), view='remove_confirmation')

        error_div = browser.css('div.documents div.error').first
        self.assertEqual('The document is not trashed.', error_div.text)
        self.assertEqual([u'L\xe4\xe4r'], error_div.parent().css('a').text)

    @browsing
    def test_when_deletion_is_possible_confirmation_message_is_show(self, browser):
        self.login(self.manager, browser)

        self.trash_documents(self.empty_document)
        browser.open(self.dossier, self.make_path_param(self.empty_document), view='remove_confirmation')

        message = browser.css('.message').first
        self.assertEqual('Warning Do you really want to delete the selected documents?', message.text)
        self.assertEqual('message warning', message.get('class'))

    @browsing
    def test_confirm_deletion(self, browser):
        self.login(self.manager, browser)

        self.trash_documents(self.empty_document)
        browser.open(self.dossier, self.make_path_param(self.empty_document), view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEqual(Document.removed_state, api.content.get_state(obj=self.empty_document))

    @browsing
    def test_after_deletion_redirects_back_and_shows_statusmessage(self, browser):
        self.login(self.manager, browser)

        self.trash_documents(self.empty_document)
        browser.open(self.dossier, self.make_path_param(self.empty_document), view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEqual('{}#trash'.format(self.dossier.absolute_url()), browser.url)
        assert_message('The documents have been successfully deleted')

    @browsing
    def test_deletion_works_also_for_mails(self, browser):
        self.login(self.manager, browser)

        self.trash_documents(self.mail_eml)
        browser.open(self.dossier, self.make_path_param(self.mail_eml), view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEqual(OGMail.removed_state, api.content.get_state(obj=self.mail_eml))

    @browsing
    def test_form_is_csrf_safe(self, browser):
        self.login(self.manager, browser)

        url = '{}/remove_confirmation?paths:list={}&form.buttons.remove=true'.format(
            self.dossier.absolute_url(), '/'.join(self.empty_document.getPhysicalPath()))

        with browser.expect_unauthorized():
            browser.open(url)


class TestRemoveJournalization(IntegrationTestCase):

    def test_removing_is_journalized_on_object(self):
        self.login(self.manager)

        self.trash_documents(self.empty_document, self.mail_eml)
        Remover([self.empty_document, self.mail_eml]).remove()

        self.assert_journal_entry(self.mail_eml, OBJECT_REMOVED, u'Document Die B\xfcrgschaft removed.')
        self.assert_journal_entry(self.empty_document, OBJECT_REMOVED, u'Document L\xe4\xe4r removed.')

    def test_removing_is_journalized_on_parent(self):
        self.login(self.manager)

        self.trash_documents(self.empty_document, self.mail_eml)
        Remover([self.empty_document, self.mail_eml]).remove()

        self.assert_journal_entry(self.subdossier, OBJECT_REMOVED, u'Document L\xe4\xe4r removed.')
        self.assert_journal_entry(self.dossier, OBJECT_REMOVED, u'Document Die B\xfcrgschaft removed.')


class TestRestoreJournalization(IntegrationTestCase):

    def setUp(self):
        super(TestRestoreJournalization, self).setUp()

        self.login(self.manager)

        self.trash_documents(self.empty_document, self.mail_eml)
        Remover([self.empty_document, self.mail_eml]).remove()

        api.content.transition(obj=self.mail_eml, transition=self.mail_eml.restore_transition)
        api.content.transition(obj=self.empty_document, transition=self.empty_document.restore_transition)

    def test_restoring_is_journalized_on_object(self):
        self.assert_journal_entry(self.mail_eml, OBJECT_RESTORED, u'Document Die B\xfcrgschaft restored.')
        self.assert_journal_entry(self.empty_document, OBJECT_RESTORED, u'Document L\xe4\xe4r restored.')

    def test_restoring_is_journalized_on_parent(self):
        self.assert_journal_entry(self.subdossier, OBJECT_RESTORED, u'Document L\xe4\xe4r restored.')
        self.assert_journal_entry(self.dossier, OBJECT_RESTORED, u'Document Die B\xfcrgschaft restored.')
