from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from opengever.testing import SolrIntegrationTestCase
from plone.namedfile.file import NamedBlobFile
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
    def test_cancel_checkout_for_document_without_initial_version_is_ignored(self, browser):
        doc = create(Builder('document').within(self.dossier).checked_out())
        browser.login().open(doc, {'_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals(None, self.get_manager(doc).get_checked_out_by())

    @browsing
    def test_cancel_reset_changes_on_working_copy(self, browser):
        doc = create(Builder('document').within(self.dossier)
                     .with_dummy_content()
                     .checked_out())

        doc.file = NamedBlobFile(data='New', filename=u'test.txt')

        browser.login().open(doc, {'_authenticator': createToken()},
                             view='cancel_document_checkouts', )

        self.assertEquals('Test data', doc.file.data)
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


class TestCancelDocumentCheckoutConfirmation(SolrIntegrationTestCase):

    @browsing
    def test_cancel_checkout_action_needs_confirmation(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)

        manager.checkout()
        self.assertEqual('kathi.barfuss', manager.get_checked_out_by())

        browser.open(self.document, view="tabbedview_view-overview")
        browser.click_on("Cancel checkout")
        self.assertEqual('kathi.barfuss', manager.get_checked_out_by())

        browser.click_on("Cancel checkout")
        self.assertEqual(None, manager.get_checked_out_by())
        assert_message(u"Cancel checkout: Vertr\xe4gsentwurf")

    @browsing
    def test_cancel_checkouts_action_needs_confirmation(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)

        manager.checkout()
        browser.open(self.dossier, view="tabbedview_view-documents-proxy")
        self.assertEqual('cancel_documents_checkout_confirmation:method',
                         browser.find("Cancel").get("href"))

        paths = [self.document.absolute_url_path(),
                 self.subdocument.absolute_url_path()]
        browser.open(self.dossier,
                     {'paths': paths,
                      '_authenticator': createToken()},
                     view='cancel_documents_checkout_confirmation', )
        self.assertEqual('kathi.barfuss', manager.get_checked_out_by())
        browser.click_on("Cancel checkout")
        self.assertEqual(None, manager.get_checked_out_by())
