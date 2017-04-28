from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from plone.protect import createToken
from zope.component import getMultiAdapter


class TestCancelDocuments(FunctionalTestCase):

    def setUp(self):
        super(TestCancelDocuments, self).setUp()
        repo_root = create(Builder('repository_root'))
        repo_folder = create(Builder('repository').within(repo_root))
        self.dossier = create(Builder('dossier').within(repo_folder))

    def obj2paths(self, objs):
        return ['/'.join(obj.getPhysicalPath()) for obj in objs]

    def get_manager(self, doc):
        return getMultiAdapter(
            (doc, self.portal.REQUEST), ICheckinCheckoutManager)

    @browsing
    def test_shows_message_if_view_is_called_on_a_dossier_without_passing_paths(self, browser):
        browser.login().open(self.dossier, view='cancel_document_checkouts')
        self.assertEquals(['You have not selected any documents.'],
                          error_messages())

    @browsing
    def test_cancel_checkout_for_document_when_view_is_called_on_a_document(self, browser):
        doc = create(Builder('document').within(self.dossier).checked_out())
        browser.login().open(doc, {'_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(None, self.get_manager(doc).get_checked_out_by())

    @browsing
    def test_cancel_checkout_for_all_selected_documents(self, browser):
        doc1 = create(Builder('document').within(self.dossier).checked_out())
        doc2 = create(Builder('document').within(self.dossier).checked_out())

        browser.login().open(self.dossier,
                             {'paths': self.obj2paths([doc1, doc2]),
                              '_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(None, self.get_manager(doc1).get_checked_out_by())
        self.assertEquals(None, self.get_manager(doc2).get_checked_out_by())

    @browsing
    def test_redirects_to_document_itself_when_view_is_called_on_a_document(self, browser):
        doc = create(Builder('document').within(self.dossier).checked_out())
        browser.login().open(doc, {'_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(doc, browser.context)
        self.assertEquals([u'Cancel checkout: Testdokum\xe4nt'],
                          info_messages())

    @browsing
    def test_redirects_to_dossier_when_multiple_documents_are_selected(self, browser):
        doc1 = create(Builder('document').within(self.dossier).checked_out())
        doc2 = create(Builder('document')
                      .within(self.dossier)
                      .titled(u'Anfrage Baugesuch Herr Meier')
                      .checked_out())

        browser.login().open(self.dossier,
                             {'paths': self.obj2paths([doc1, doc2]),
                              '_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(self.dossier, browser.context)
        self.assertEquals([u'Cancel checkout: Testdokum\xe4nt',
                           u'Cancel checkout: Anfrage Baugesuch Herr Meier'],
                          info_messages())

    @browsing
    def test_shows_message_when_checkout_cant_be_cancelled(self, browser):
        doc = create(Builder('document').within(self.dossier))

        browser.login().open(doc, {'_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(
            [u'Could not cancel checkout on document Testdokum\xe4nt.'],
            error_messages())

    @browsing
    def test_shows_message_when_mails_are_selected(self, browser):
        doc = create(Builder('document').within(self.dossier).checked_out())
        mail = create(Builder('mail').with_dummy_message().within(self.dossier))

        browser.login().open(self.dossier,
                             {'paths': self.obj2paths([doc, mail]),
                              '_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(self.dossier, browser.context)
        self.assertEquals([u'Could not cancel checkout on document [No Subject], '
                           'mails does not support the checkin checkout process.'],
                          error_messages())
