from AccessControl.Permission import Permission
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.trash.remover import Remover
from opengever.trash.trash import ITrashed
from opengever.trash.trash import ITrasher
from opengever.trash.trash import TrashError
from plone import api
from plone.protect import createToken
from zExceptions import Unauthorized
from zope.interface import noLongerProvides


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

    @browsing
    def test_trashing_non_trashable_item_is_not_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.task)
        data['_authenticator'] = createToken()
        browser.open(self.dossier, view="trash_content", data=data)
        self.assertEquals(
            [u'The object {} is not trashable.'.format(self.task.title)],
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
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_mail_can_be_trashed(self):
        self.login(self.manager)
        obj = self.mail_eml
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_private_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.private_document
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_private_mail_can_be_trashed(self):
        self.login(self.manager)
        obj = self.private_mail
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_inbox_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_document
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_forwarding_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_forwarding_document
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_task_document_can_be_trashed(self):
        self.login(self.manager)
        obj = self.taskdocument
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_proposal_document_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.proposaldocument
        trasher = ITrasher(obj)
        with self.assertRaises(Unauthorized):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_document_template_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.docprops_template
        trasher = ITrasher(obj)
        with self.assertRaises(Unauthorized):
            trasher.trash()
        self.assertFalse(ITrashed.providedBy(obj))

    def test_dossier_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.empty_dossier
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_task_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.info_task
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_repofolder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.empty_repofolder
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_disposition_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.disposition
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_proposal_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.proposal
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_template_folder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.templates
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_dossier_template_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.dossiertemplate
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_workspace_root_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace_root
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_workspace_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_todo_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.todo
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_todolist_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.todolist_general
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_workspace_meeting_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace_meeting
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_private_folder_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.private_folder
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_private_dossier_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.private_dossier
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_inbox_container_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_container
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_inbox_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))

    def test_forwarding_cannot_be_trashed(self):
        self.login(self.manager)
        obj = self.inbox_forwarding
        trasher = ITrasher(obj)
        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Not trashable', str(exc.exception))
        self.assertFalse(ITrashed.providedBy(obj))


class TestWorkspaceFolderTrasher(IntegrationTestCase):

    def test_workspace_folder_can_be_trashed(self):
        self.login(self.manager)
        obj = self.workspace_folder
        trasher = ITrasher(obj)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(obj))

    def test_trashing_workspace_folder_is_recursive(self):
        self.login(self.manager)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))
        subdocument = create(Builder('document')
                             .titled(u'Subdocument')
                             .within(subfolder))

        self.assertFalse(ITrashed.providedBy(self.workspace_folder))
        self.assertFalse(ITrashed.providedBy(self.workspace_folder_document))
        self.assertFalse(ITrashed.providedBy(subfolder))
        self.assertFalse(ITrashed.providedBy(subdocument))

        trasher = ITrasher(self.workspace_folder)
        trasher.trash()

        self.assertTrue(ITrashed.providedBy(self.workspace_folder))
        self.assertTrue(ITrashed.providedBy(self.workspace_folder_document))
        self.assertTrue(ITrashed.providedBy(subfolder))
        self.assertTrue(ITrashed.providedBy(subdocument))

    def test_cannot_trash_workspace_folder_containing_a_checked_out_document(self):
        self.login(self.manager)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))
        subdocument = create(Builder('document')
                             .titled(u'Subdocument')
                             .within(subfolder))

        trasher = ITrasher(self.workspace_folder)
        self.assertTrue(trasher.verify_may_trash())

        self.checkout_document(subdocument)

        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Document checked out', str(exc.exception))

    def test_cannot_trash_workspace_folder_containing_a_subfolder_with_insufficient_permissions(self):
        self.login(self.workspace_member)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))
        subdocument = create(Builder('document')
                             .titled(u'Subdocument')
                             .within(subfolder))

        trasher = ITrasher(self.workspace_folder)
        self.assertTrue(trasher.verify_may_trash())

        subfolder.__ac_local_roles_block__ = True

        self.login(self.workspace_admin)
        with self.assertRaises(Unauthorized):
            trasher.trash()

    def test_untrashing_workspace_folder_is_recursive(self):
        self.login(self.manager)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))
        subdocument = create(Builder('document')
                             .titled(u'Subdocument')
                             .within(subfolder))

        trasher = ITrasher(self.workspace_folder)
        trasher.trash()
        trasher.untrash()

        self.assertFalse(ITrashed.providedBy(self.workspace_folder))
        self.assertFalse(ITrashed.providedBy(self.workspace_folder_document))
        self.assertFalse(ITrashed.providedBy(subfolder))
        self.assertFalse(ITrashed.providedBy(subdocument))

    def test_cannot_untrash_workspace_folder_containing_an_untrashed_document(self):
        self.login(self.manager)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))
        subdocument = create(Builder('document')
                             .titled(u'Subdocument')
                             .within(subfolder))

        trasher = ITrasher(self.workspace_folder)
        trasher.trash()
        self.assertTrue(trasher.verify_may_untrash())

        noLongerProvides(subdocument, ITrashed)

        with self.assertRaises(Unauthorized):
            trasher.untrash()

    def test_cannot_untrash_object_with_trashed_parent(self):
        self.login(self.manager)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))

        trasher = ITrasher(self.workspace_folder)
        trasher.trash()
        self.assertTrue(trasher.verify_may_untrash())

        subfolder_trasher = ITrasher(subfolder)
        with self.assertRaises(Unauthorized):
            subfolder_trasher.verify_may_untrash()

        document_trasher = ITrasher(self.workspace_folder_document)
        with self.assertRaises(Unauthorized):
            document_trasher.verify_may_untrash()

        noLongerProvides(self.workspace_folder, ITrashed)
        self.assertTrue(subfolder_trasher.verify_may_untrash())
        self.assertTrue(document_trasher.verify_may_untrash())

    def test_cannot_trash_trashed_workspace_folder(self):
        self.login(self.manager)
        trasher = ITrasher(self.workspace_folder)
        trasher.trash()

        with self.assertRaises(TrashError) as exc:
            trasher.trash()
        self.assertEqual('Already trashed', str(exc.exception))

    def test_can_trash_workspace_folder_containing_trashed_objects(self):
        self.login(self.manager)
        subfolder = create(Builder('workspace folder')
                           .titled(u'Subfolder')
                           .within(self.workspace_folder))

        ITrasher(self.workspace_document).trash()
        ITrasher(subfolder).trash()

        trasher = ITrasher(self.workspace_folder)
        trasher.trash()
        self.assertTrue(ITrashed.providedBy(self.workspace_folder))
