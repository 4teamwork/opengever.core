from AccessControl.Permission import Permission
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.trash.remover import Remover
from opengever.trash.trash import ITrashableMarker
from opengever.trash.trash import ITrashed
from opengever.trash.trash import ITrasher
from plone import api
from plone.protect import createToken
from zExceptions import Unauthorized


class TestTrash(IntegrationTestCase):

    @browsing
    def test_trash_items_mark_items_as_trashed(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trash_content", data=data)

        self.assertFalse(ITrashed.providedBy(self.document))
        self.assertFalse(obj2brain(self.document).trashed)

        self.assertTrue(ITrashed.providedBy(self.subdocument))
        self.assertTrue(obj2brain(self.subdocument, unrestricted=True).trashed)

    @browsing
    def test_shows_statusmessage_and_redirects_to_documents_tab(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.subdocument)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trash_content", data=data)

        self.assertEquals(
            [u'Object {} has been moved to the trash.'.format(self.subdocument.title)],
            info_messages())
        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)

    @browsing
    def test_shows_statusmessage_on_trashed_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
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
            view="trash_content",
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
            view="trash_content",
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
            view="trash_content",
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
            view="trash_content",
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml)
        self.assertEqual(['This email was moved to the trash.'], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_trashed_mail_eml(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
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
            view="trash_content",
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
            view="trash_content",
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
            view="trash_content",
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg)
        self.assertEqual(['This email was moved to the trash.'], warning_messages())

    @browsing
    def test_does_not_show_statusmessage_on_next_view_after_viewing_trashed_mail_msg(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
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
            view="trash_content",
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
            view="trash_content",
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='tabbedview_view-overview')
        browser.open(self.dossier)
        self.assertEqual([], warning_messages())

    @browsing
    def test_redirect_back_and_shows_message_when_no_items_is_selected(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view="trash_content")

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
        browser.open(self.dossier, view="trash_content", data=data)

        self.assertEquals(
            [u'Object {} is already in the trash.'.format(
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
        browser.open(self.dossier, view="trash_content", data=data)

        self.assertEquals(
            [u"Could not move document {} to the trash: it's currently checked out.".format(
                self.subdocument.title)],
            error_messages())
        self.assertEquals(
            '{}#documents'.format(self.dossier.absolute_url()), browser.url)


class TestUntrash(IntegrationTestCase):

    @browsing
    def test_redirect_back_and_shows_message_when_no_items_is_selected(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view="untrash_content")

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
        browser.open(self.dossier, view="untrash_content", data=data)

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
        browser.open(self.dossier, view="untrash_content", data=data)

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
        browser.open(self.dossier, view="untrash_content", data=data)

        self.assertEquals(
            [u'Restoring object {} from trash is not allowed.'.format(self.subdocument.title)],
            error_messages())

    @browsing
    def test_error_when_untrashing_removed_document(self, browser):
        self.login(self.manager, browser=browser)

        data = self.make_path_param(self.empty_document)
        data['_authenticator'] = createToken()

        self.trash_documents(self.empty_document)
        Remover([self.empty_document]).remove()

        # Removed document cannot be untrashed
        browser.open(self.empty_dossier, view="untrash_content", data=data)

        self.assertTrue(ITrashed.providedBy(self.empty_document))
        self.assertEquals(
            [u'Restoring object {} from trash is not allowed.'.format(self.empty_document.title)],
            error_messages())

        # When restored, document can be untrashed
        api.content.transition(
            obj=self.empty_document,
            transition=self.empty_document.restore_transition)

        self.assertEqual(self.empty_document.active_state,
                         api.content.get_state(self.empty_document))

        browser.open(self.empty_dossier, view="untrash_content", data=data)
        self.assertFalse(ITrashed.providedBy(self.empty_document))


class TestTrashWithBumblebee(IntegrationTestCase):

    features = ('bumblebee',)

    @browsing
    def test_shows_statusmessage_on_trashed_document_bumblebee_document_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
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
            view="trash_content",
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
        browser.open(
            self.dossier,
            view="trash_content",
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
            view="trash_content",
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml, view='bumblebee-overlay-document')
        self.assertEqual(
            ['This email was moved to the trash.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_eml_bumblebee_listing_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
            data=self.make_path_param(self.mail_eml),
            send_authenticator=True,
        )
        browser.open(self.mail_eml, view='bumblebee-overlay-listing')
        self.assertEqual(
            ['This email was moved to the trash.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_msg_bumblebee_document_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='bumblebee-overlay-document')
        self.assertEqual(
            ['This email was moved to the trash.'],
            browser.css('.portalMessage.warning dd').text,
        )

    @browsing
    def test_shows_statusmessage_on_trashed_mail_msg_bumblebee_listing_overlay(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier,
            view="trash_content",
            data=self.make_path_param(self.mail_msg),
            send_authenticator=True,
        )
        browser.open(self.mail_msg, view='bumblebee-overlay-listing')
        self.assertEqual(
            ['This email was moved to the trash.'],
            browser.css('.portalMessage.warning dd').text,
        )


class TestTrasher(IntegrationTestCase):

    def test_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.document
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_mail_can_be_trashed(self):
        self.login(self.manager)
        obj = self.mail_eml
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_private_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.private_document
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_private_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.private_document
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_private_mail_can_be_trashed(self):
        self.login(self.manager)
        obj = self.private_mail
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_inbox_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_document
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_forwarding_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_forwarding_document
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_task_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.taskdocument
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_proposal_document_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.proposaldocument
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(Unauthorized):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_document_template_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.docprops_template
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(Unauthorized):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_dossier_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.empty_dossier
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_task_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.info_task
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_repofolder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.empty_repofolder
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_disposition_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.disposition
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_proposal_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.proposal
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_template_folder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.templates
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(Unauthorized):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_dossier_template_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.dossiertemplate
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_workspace_root_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace_root
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_workspace_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(Unauthorized):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_workspace_folder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace_folder
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_todo_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.todo
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_todolist_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.todolist_general
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_workspace_meeting_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace_meeting
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_private_folder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.private_folder
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_private_dossier_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.private_dossier
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_inbox_container_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_container
        self.assertFalse(ITrashableMarker.providedBy(obj))

    def test_inbox_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_forwarding_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_forwarding
        self.assertTrue(ITrashableMarker.providedBy(obj))
        trasher = ITrasher(obj)
        with self.assertRaises(AttributeError):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))
