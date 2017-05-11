from AccessControl.Permission import Permission
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.trash.trash import ITrashed
from plone.protect import createToken
import transaction


class TestTrash(FunctionalTestCase):

    def setUp(self):
        super(TestTrash, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_trash_items_mark_items_as_trashed(self, browser):
        document_a = create(Builder('document')
                            .within(self.dossier)
                            .titled(u'Dokum\xe4nt A'))
        document_b = create(Builder('document')
                            .within(self.dossier)
                            .titled(u'Dokum\xe4nt B'))

        data = {'paths:list': ['/'.join(document_b.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="trashed", data=data)

        self.assertFalse(ITrashed.providedBy(document_a))
        self.assertFalse(obj2brain(document_a).trashed)

        self.assertTrue(ITrashed.providedBy(document_b))
        self.assertTrue(obj2brain(document_b, unrestricted=True).trashed)

    @browsing
    def test_shows_statusmessage_and_redirects_to_documents_tab(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'Dokum\xe4nt A'))

        data = {'paths:list': ['/'.join(document.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="trashed", data=data)

        self.assertEquals([u'the object Dokum\xe4nt A trashed'],
                          info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)

    @browsing
    def test_redirect_back_and_shows_message_when_no_items_is_selected(self, browser):
        browser.login().open(self.dossier, view="trashed")

        self.assertEquals(['You have not selected any items.'],
                          error_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)

    @browsing
    def test_trashing_already_trashed_items_is_not_possible(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .trashed()
                          .titled(u'Dokum\xe4nt C'))

        data = {'paths:list': ['/'.join(document.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="trashed", data=data)

        self.assertEquals(
            [u'could not trash the object Dokum\xe4nt C, it is already trashed'],
            error_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)

    @browsing
    def test_trashing_checked_out_documents_is_not_possible(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .checked_out()
                          .titled(u'Dokum\xe4nt C'))

        data = {'paths:list': ['/'.join(document.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="trashed", data=data)

        self.assertEquals(
            [u'could not trash the object Dokum\xe4nt C, it is checked out.'],
            error_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)

    @browsing
    def test_error_for_untrashable_documents(self, browser):
        trashable = create(Builder('document')
                           .within(self.dossier)
                           .titled(u'Trashable document'))
        untrashable = create(Builder('document')
                             .within(self.dossier)
                             .titled(u'Untrashable document'))
        # Remove trash permission from all users.
        Permission('opengever.trash: Trash content', [], untrashable).setRoles(())
        transaction.commit()

        data = {'paths:list': ['/'.join(trashable.getPhysicalPath()),
                               '/'.join(untrashable.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="trashed", data=data)

        self.assertEquals([u'the object Trashable document trashed'],
                          info_messages())
        self.assertEquals([u'Trashing Untrashable document is forbidden'],
                          error_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)


class TestUntrash(FunctionalTestCase):

    def setUp(self):
        super(TestUntrash, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_redirect_back_and_shows_message_when_no_items_is_selected(self, browser):
        browser.login().open(self.dossier, view="untrashed")

        self.assertEquals(['You have not selected any items.'],
                          error_messages())
        self.assertEquals('http://nohost/plone/dossier-1#trash', browser.url)

    @browsing
    def test_untrash_unmark_document(self, browser):
        document_a = create(Builder('document')
                            .within(self.dossier)
                            .trashed()
                            .titled(u'Dokum\xe4nt A'))
        document_b = create(Builder('document')
                            .within(self.dossier)
                            .trashed()
                            .titled(u'Dokum\xe4nt B'))

        data = {'paths:list': ['/'.join(document_a.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="untrashed", data=data)

        self.assertFalse(ITrashed.providedBy(document_a))
        self.assertFalse(obj2brain(document_a).trashed)

        self.assertTrue(ITrashed.providedBy(document_b))
        self.assertTrue(obj2brain(document_b, unrestricted=True).trashed)

    @browsing
    def test_redirects_to_documents_tab(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .trashed()
                          .titled(u'Dokum\xe4nt A'))

        data = {'paths:list': ['/'.join(document.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="untrashed", data=data)

        self.assertEquals(
            'http://nohost/plone/dossier-1#documents', browser.url)

    @browsing
    def test_error_when_untrashing_not_allowed(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .trashed()
                          .titled(u'The document'))
        # Remove trash permission from all users.
        Permission('opengever.trash: Untrash content',
                   [], document).setRoles(())
        transaction.commit()

        data = {'paths:list': ['/'.join(document.getPhysicalPath())],
                '_authenticator': createToken()}
        browser.login().open(self.dossier, view="untrashed", data=data)

        self.assertEquals([u'Untrashing The document is forbidden'],
                          error_messages())
