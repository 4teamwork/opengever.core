from AccessControl import Unauthorized
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from opengever.trash.remover import Remover
from plone import api
from plone.app.testing import setRoles
import transaction


class TestRemover(FunctionalTestCase):

    def setUp(self):
        super(TestRemover, self).setUp()
        self.grant('Administrator')

    def test_changes_state_to_removed_for_all_documents(self):
        doc1 = create(Builder('document').trashed())
        doc2 = create(Builder('document').trashed())

        Remover([doc1, doc2]).remove()

        self.assertEquals('document-state-removed',
                          api.content.get_state(obj=doc1))
        self.assertEquals('document-state-removed',
                          api.content.get_state(obj=doc2))

    def test_raises_runtimeerror_when_preconditions_are_not_satisified(self):
        doc1 = create(Builder('document').trashed())
        doc2 = create(Builder('document'))

        with self.assertRaises(RuntimeError) as cm:
            Remover([doc1, doc2]).remove()

        self.assertEquals('RemoveConditions not satisified',
                          str(cm.exception))

    def test_raises_unauthorized_when_user_has_not_remove_permission(self):
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

        self.grant('Editor')
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
            ["Error The selected documents can't be removed, see errors messages above."],
            browser.css('.message').text)

    @browsing
    def test_shows_specific_message_on_documents_error_box(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc2])}
        browser.login().open(self.dossier, data, view='remove_confirmation')

        error_div = browser.css('div.documents div.error').first
        self.assertEquals('The documents is not trashed.', error_div.text)
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

        self.assertEquals('document-state-removed',
                          api.content.get_state(obj=self.doc1))
        self.assertEquals('document-state-removed',
                          api.content.get_state(obj=self.doc3))

    @browsing
    def test_after_deletion_redirects_back_and_shows_statusmessage(self, browser):
        data = {'paths': self.obj2paths([self.doc1, self.doc3])}
        browser.login().open(self.dossier, data, view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEquals('http://nohost/plone/dossier-1#trash', browser.url)
        assert_message('The documents are succesfully deleted')

    @browsing
    def test_deletion_works_also_for_mails(self, browser):
        mail = create(Builder('mail')
                      .trashed()
                      .within(self.dossier))
        data = {'paths': self.obj2paths([mail, self.doc1])}
        browser.login().open(self.dossier, data, view='remove_confirmation')
        browser.forms.get('remove_confirmation').submit()

        self.assertEquals('mail-state-removed',
                          api.content.get_state(obj=mail))
