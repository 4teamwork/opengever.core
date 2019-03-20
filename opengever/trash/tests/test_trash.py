from AccessControl.Permission import Permission
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.trash.remover import Remover
from opengever.trash.trash import ITrashed
from plone import api
from plone.protect import createToken


class TestTrash(IntegrationTestCase):

    @browsing
    def test_trash_items_mark_items_as_trashed(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trashed", data=data)

        self.assertFalse(ITrashed.providedBy(self.document))
        self.assertFalse(obj2brain(self.document).trashed)

        self.assertTrue(ITrashed.providedBy(self.subdocument))
        self.assertTrue(obj2brain(self.subdocument, unrestricted=True).trashed)

    @browsing
    def test_shows_statusmessage_and_redirects_to_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trashed", data=data)

        self.assertEquals(
            [u'the object {} trashed'.format(self.subdocument.title)],
            info_messages())
        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_shows_statusmessage_on_trashed_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument)
        self.assertEqual(['This document is trashed.'], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_trashed_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument)
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_tab_of_trashed_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument, view='tabbedview_view-overview')
        self.assertEqual([], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_a_tab_of_a_trashed_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument, view='tabbedview_view-overview')
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_shows_statusmessage_on_trashed_mail_eml(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml)
        self.assertEqual(['This mail is trashed.'], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_trashed_mail_eml(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml)
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_tab_of_trashed_mail_eml(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml, view='tabbedview_view-overview')
        self.assertEqual([], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_a_tab_of_a_trashed_mail_eml(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml, view='tabbedview_view-overview')
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_shows_statusmessage_on_trashed_mail_msg(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg)
        self.assertEqual(['This mail is trashed.'], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_trashed_mail_msg(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg)
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_tab_of_trashed_mail_msg(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='tabbedview_view-overview')
        self.assertEqual([], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_a_tab_of_a_trashed_mail_msg(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='tabbedview_view-overview')
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_redirect_back_and_shows_message_when_no_items_is_selected(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view="trashed")

        self.assertEquals(['You have not selected any items.'],
                          error_messages())
        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_trashing_already_trashed_items_is_not_possible(self, browser):
        self.login(self.regular_user, browser=browser)
        self.trash_documents(self.subdocument)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trashed", data=data)

        self.assertEquals(
            [u'could not trash the object {}, it is already trashed'.format(
                self.subdocument.title)],
            error_messages())
        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_trashing_checked_out_documents_is_not_possible(self, browser):
        self.login(self.regular_user, browser=browser)
        self.checkout_document(self.subdocument)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trashed", data=data)

        self.assertEquals(
            [u'could not trash the object {}, it is checked out.'.format(
                self.subdocument.title)],
            error_messages())
        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)


class TestUntrash(IntegrationTestCase):

    @browsing
    def test_redirect_back_and_shows_message_when_no_items_is_selected(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view="untrashed")

        self.assertEquals(['You have not selected any items.'],
                          error_messages())
        self.assertEquals(
            '{}#trash'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_untrash_unmark_document(self, browser):
        self.login(self.regular_user, browser=browser)

        self.trash_documents(self.taskdocument, self.subdocument)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="untrashed", data=data)

        self.assertFalse(ITrashed.providedBy(self.subdocument))
        self.assertFalse(obj2brain(self.subdocument).trashed)

        self.assertTrue(ITrashed.providedBy(self.taskdocument))
        self.assertTrue(obj2brain(self.taskdocument, unrestricted=True).trashed)

    @browsing
    def test_redirects_to_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        self.trash_documents(self.subdocument)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="untrashed", data=data)

        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_error_when_untrashing_not_allowed(self, browser):
        self.login(self.regular_user, browser=browser)

        self.trash_documents(self.subdocument)

        # Remove trash permission from all users.
        Permission(
            'opengever.trash: Untrash content', [], self.subdocument).setRoles(())

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="untrashed", data=data)

        self.assertEquals(
            [u'Untrashing {} is forbidden'.format(self.subdocument.title)],
            error_messages())

    @browsing
    def test_error_when_untrashing_removed_document(self, browser):
        self.login(self.manager, browser=browser)

        data = self.make_path_param(self.empty_document)
        data['_authenticator'] = createToken()

        self.trash_documents(self.empty_document)
        Remover([self.empty_document]).remove()

        # Removed document cannot be untrashed
        browser.open(self.empty_dossier, view="untrashed", data=data)

        self.assertTrue(ITrashed.providedBy(self.empty_document))
        self.assertEquals(
            [u'Untrashing {} is forbidden'.format(self.empty_document.title)],
            error_messages())

        # When restored, document can be untrashed
        api.content.transition(
            obj=self.empty_document,
            transition=self.empty_document.restore_transition)

        self.assertEqual(self.empty_document.active_state,
                         api.content.get_state(self.empty_document))

        browser.open(self.empty_dossier, view="untrashed", data=data)
        self.assertFalse(ITrashed.providedBy(self.empty_document))


class TestTrashWithBumblebee(IntegrationTestCase):

    features = ('bumblebee',)

    @browsing
    def test_shows_statusmessage_on_trashed_document_bumblebee_document_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument, view='bumblebee-overlay-document')
        self.assertEqual(
            ['This document is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_document_bumblebee_listing_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument, view='bumblebee-overlay-listing')
        self.assertEqual(
            ['This document is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_document_bumblebee_version_listing_overlay(self, browser):
        self.login(self.regular_user, browser)
        # Ensure we have two versions of the document
        self.checkout_document(self.subdocument)
        self.checkin_document(self.subdocument)
        self.checkout_document(self.subdocument)
        self.checkin_document(self.subdocument)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.subdocument),
            send_authenticator=True,
        )
        browser.open(self.subdocument, view='bumblebee-overlay-listing?version_id=0')
        self.assertEqual(
            ['This document is trashed.', 'You are looking at a versioned file.'],
            browser.css('.portalMessage.warning dd').text,
        )
        browser.open(self.subdocument, view='bumblebee-overlay-listing?version_id=1')
        self.assertEqual(
            ['This document is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_eml_bumblebee_document_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml, view='bumblebee-overlay-document')
        self.assertEqual(
            ['This mail is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_eml_bumblebee_listing_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml, view='bumblebee-overlay-listing')
        self.assertEqual(
            ['This mail is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_msg_bumblebee_document_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='bumblebee-overlay-document')
        self.assertEqual(
            ['This mail is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_msg_bumblebee_listing_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view='trashed',
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='bumblebee-overlay-listing')
        self.assertEqual(
            ['This mail is trashed.'],
            browser.css('.portalMessage.warning dd').text,
        )
