from AccessControl import Unauthorized
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from opengever.document.document import Document
from opengever.journal.handlers import OBJECT_REMOVED
from opengever.journal.handlers import OBJECT_RESTORED
from opengever.mail.mail import OGMail
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from opengever.trash.remover import Remover
from plone import api
from plone.app.testing import setRoles
import transaction


class TestRemover(FunctionalTestCase):

    def setUp(self):
        super(TestRemover, self).setUp()
        # Only manager has 'Delete GEVER content' permission by default
        self.grant('Manager')

    def test_changes_state_to_removed_for_all_documents(self):
        doc1 = create(Builder('document').trashed())
        doc2 = create(Builder('document').trashed())

        Remover([doc1, doc2]).remove()

        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=doc1))
        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=doc2))

    def test_raises_runtimeerror_when_preconditions_are_not_satisified(self):
        doc1 = create(Builder('document').trashed())
        doc2 = create(Builder('document'))

        with self.assertRaises(RuntimeError) as cm:
            Remover([doc1, doc2]).remove()

        self.assertEquals('RemoveConditions not satisified',
                          str(cm.exception))

    def test_raises_unauthorized_when_user_does_not_have_remove_permission(self):
        doc1 = create(Builder('document').trashed())

        create_plone_user(self.portal, 'hugo.boss')
        self.login(user_id='hugo.boss')
        setRoles(self.portal, 'hugo.boss', ['Member'])
        transaction.commit()

        with self.assertRaises(Unauthorized):
            Remover([doc1]).remove()


class TestRemoveConfirmationView(FunctionalTestCase):

    def setUp(self):
        super(TestRemoveConfirmationView, self).setUp()

        # Only manager has 'Delete GEVER content' permission by default
        self.grant('Manager')
        self.dossier = create(Builder('dossier'))

        self.doc1 = create(Builder('document')
                           .titled(u'Document 1')
                           .within(self.dossier)
                           .trashed())

        self.doc2 = create(Builder('document')
                           .titled(u'Document 2')
                           .within(self.dossier))

        self.doc3 = create(Builder('document')
                           .titled(u'Document 3')
                           .within(self.dossier)
                           .trashed())

    def obj2paths(self, objs):
        return ['/'.join(obj.getPhysicalPath()) for obj in objs]

    @browsing
    def test_redirects_to_trash_tab_when_no_documents_selected(self, browser):
        browser.login().open(self.dossier, view='remove_confirmation')

        self.assertEquals('{}#trash'.format(self.dossier.absolute_url()),
                          browser.url)
        assert_message('You have not selected any items')

    @browsing
    def test_submit_button_is_disabled_when_preconditions_are_not_satisfied(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc2])}
        browser.login().open(self.dossier, data, view='remove_confirmation')

        self.assertEquals(
            'disabled', browser.css('#form-buttons-delete').first.get('disabled'))

    @browsing
    def test_shows_error_message_on_top(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc2])}
        browser.login().open(self.dossier, data, view='remove_confirmation')

        self.assertEquals(
            ["Error The selected documents can't be removed, see error messages below."],
            browser.css('.message').text)

    @browsing
    def test_shows_specific_message_on_documents_error_box(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc2])}
        browser.login().open(self.dossier, data, view='remove_confirmation')

        error_div = browser.css('div.documents div.error').first
        self.assertEquals('The document is not trashed.', error_div.text)
        self.assertEquals(['Document 2'], error_div.parent().css('a').text)

    @browsing
    def test_when_deletion_is_possible_confirmation_message_is_show(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc3])}
        browser.login().open(self.dossier, data, view='remove_confirmation')

        message = browser.css('.message').first

        self.assertEquals(
            'Warning Do you really want to delete the selected documents?',
            message.text)
        self.assertEquals('message warning', message.get('class'))

    @browsing
    def test_confirm_deletion(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc3])}
        browser.login().open(self.dossier, data, view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=self.doc1))
        self.assertEquals(Document.removed_state,
                          api.content.get_state(obj=self.doc3))

    @browsing
    def test_after_deletion_redirects_back_and_shows_statusmessage(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc3])}
        browser.login().open(self.dossier, data, view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEquals('http://nohost/plone/dossier-1#trash', browser.url)
        assert_message('The documents have been successfully deleted')

    @browsing
    def test_deletion_works_also_for_mails(self, browser):
        mail = create(Builder('mail')
                      .trashed()
                      .within(self.dossier))
        data = {'paths': self.obj2paths([mail, self.doc1])}
        browser.login().open(self.dossier, data, view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEquals(OGMail.removed_state,
                          api.content.get_state(obj=mail))

    @browsing
    def test_form_is_csrf_safe(self, browser):
        url = '{}/remove_confirmation?paths:list={}&form.buttons.remove=true'.format(
            self.dossier.absolute_url(),
            '/'.join(self.doc1.getPhysicalPath()))

        with self.assertRaises(Unauthorized):
            browser.login().open(url)


class TestRemoveJournalization(FunctionalTestCase):

    def setUp(self):
        super(TestRemoveJournalization, self).setUp()

        # Only manager has 'Delete GEVER content' permission by default
        self.grant('Manager')

        self.dossier = create(Builder('dossier'))
        self.mail = create(Builder('mail')
                           .titled(u'T\xe4st Mail')
                           .within(self.dossier)
                           .trashed())
        self.document = create(Builder('document')
                               .titled(u'T\xe4st Doc')
                               .within(self.dossier)
                               .trashed())

    def test_removing_is_journalized_on_object(self):
        Remover([self.mail, self.document]).remove()

        self.assert_journal_entry(self.mail, OBJECT_REMOVED,
                                  u'Document T\xe4st Mail removed.')
        self.assert_journal_entry(self.document, OBJECT_REMOVED,
                                  u'Document T\xe4st Doc removed.')

    def test_removing_is_journalized_on_parent(self):
        Remover([self.mail, self.document]).remove()

        self.assert_journal_entry(self.dossier, OBJECT_REMOVED,
                                  u'Document T\xe4st Doc removed.')
        self.assert_journal_entry(self.dossier, OBJECT_REMOVED,
                                  u'Document T\xe4st Mail removed.', entry=-2)


class TestRestoreJournalization(FunctionalTestCase):

    def setUp(self):
        super(TestRestoreJournalization, self).setUp()

        self.grant('Manager')

        self.dossier = create(Builder('dossier'))
        self.mail = create(Builder('mail')
                           .titled(u'T\xe4st Mail')
                           .within(self.dossier)
                           .removed()
                           .trashed())
        self.document = create(Builder('document')
                               .titled(u'T\xe4st Doc')
                               .within(self.dossier)
                               .removed()
                               .trashed())

        api.content.transition(
            obj=self.mail, transition=self.mail.restore_transition)
        api.content.transition(
            obj=self.document, transition=self.document.restore_transition)

    def test_restoring_is_journalized_on_object(self):
        self.assert_journal_entry(self.mail, OBJECT_RESTORED,
                                  u'Document T\xe4st Mail restored.')
        self.assert_journal_entry(self.document, OBJECT_RESTORED,
                                  u'Document T\xe4st Doc restored.')

    def test_restoring_is_journalized_on_parent(self):
        self.assert_journal_entry(self.dossier, OBJECT_RESTORED,
                                  u'Document T\xe4st Doc restored.')
        self.assert_journal_entry(self.dossier, OBJECT_RESTORED,
                                  u'Document T\xe4st Mail restored.', entry=-2)
