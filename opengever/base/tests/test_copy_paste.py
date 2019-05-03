from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import assignments_kept_when_copying
from opengever.base.role_assignments import ASSIGNMENT_VIA_COMMITTEE_GROUP
from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import ASSIGNMENT_VIA_PROTECT_DOSSIER
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from plone.protect import createToken
from zope.component import getUtility


class TestCopyItems(IntegrationTestCase):

    @browsing
    def test_redirects_back_and_show_message_if_no_item_was_selected(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view='copy_items')

        self.assertEqual(self.dossier.absolute_url(), browser.url)
        self.assertEqual(['You have not selected any Items.'], error_messages())

    @browsing
    def test_redirects_back_and_show_statusmessage_if_copy_success(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.document, self.mail_eml)
        browser.open(self.dossier, data=data, view='copy_items')

        self.assertEqual(self.dossier.absolute_url(), browser.url)
        self.assertEqual(['Selected objects successfully copied.'], info_messages())


class TestCopyItem(IntegrationTestCase):

    @browsing
    def test_statusmessage_if_copy_document_success(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, view='copy_item')

        self.assertEqual(self.document.absolute_url(), browser.url)
        self.assertEqual(['Selected objects successfully copied.'],
                         info_messages())

    @browsing
    def test_statusmessage_if_paste_document_success(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, view='copy_item')

        browser.open(self.empty_dossier, view='tabbed_view')
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(self.empty_dossier.absolute_url(), browser.url)
        self.assertEqual(['Objects from clipboard successfully pasted.'],
                         info_messages())

    @browsing
    def test_statusmessage_if_copy_mail_success(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml, view='copy_item')

        self.assertEqual(self.mail_eml.absolute_url(), browser.url)
        self.assertEqual(['Selected objects successfully copied.'],
                         info_messages())

    @browsing
    def test_statusmessage_if_paste_mail_success(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml, view='copy_item')

        browser.open(self.empty_dossier, view='tabbed_view')
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(self.empty_dossier.absolute_url(), browser.url)
        self.assertEqual(['Objects from clipboard successfully pasted.'],
                         info_messages())


class TestCopyPaste(IntegrationTestCase):

    @browsing
    def test_pasting_empty_clipboard_shows_message_and_redirect_back(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view='paste_clipboard')

        self.assertEqual(self.dossier.absolute_url(), browser.url)
        self.assertEqual([u"Can't paste items; the clipboard is emtpy"],
                         error_messages())

    @browsing
    def test_creates_objects_with_correct_id_format(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.document)
        browser.open(self.empty_dossier, view="copy_items", data=data)
        browser.css('#contentActionMenus a#paste').first.click()

        copy = self.empty_dossier.objectValues()[-1]
        sequence_number = getUtility(ISequenceNumber).get_number(copy)
        self.assertEquals('document-{}'.format(sequence_number), copy.getId())

    @browsing
    def test_creates_objects_with_correct_creator(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assertNotEqual(self.document.Creator(), self.regular_user.id)
        data = self.make_path_param(self.document)
        browser.open(self.empty_dossier, view="copy_items", data=data)
        browser.css('#contentActionMenus a#paste').first.click()
        copy = self.empty_dossier.objectValues()[-1]
        self.assertEqual(copy.Creator(), self.regular_user.id)
        self.assertEqual(len(copy.creators), 1)

    @browsing
    def test_pasting_handles_multiple_items_in_clipboard(self, browser):
        self.login(self.regular_user, browser=browser)

        data = self.make_path_param(self.document, self.taskdocument)
        browser.open(self.empty_dossier, view="copy_items", data=data)
        browser.css('#contentActionMenus a#paste').first.click()
        self.assertEquals(2, len(self.empty_dossier.getFolderContents()))

    @browsing
    def test_copy_document_into_dossier_succeeds(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.dossier, view="copy_items",
            data=self.make_path_param(self.document))
        browser.open(self.empty_dossier)
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(1, len(self.empty_dossier.objectValues()))
        self.assertEqual(["Objects from clipboard successfully pasted."],
                         info_messages())

    @browsing
    def test_pasting_copied_dossier_into_repository_folder_succeeds(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.empty_repofolder, view="copy_items",
            data=self.make_path_param(self.empty_dossier))
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(["Objects from clipboard successfully pasted."],
                         info_messages())
        self.assertEqual(1, len(self.empty_repofolder.objectValues()))

    @browsing
    def test_pasting_dossier_with_docs_into_repository_folder_succeeds(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('document').within(self.empty_dossier))

        browser.open(
            self.leaf_repofolder, view="copy_items",
            data=self.make_path_param(self.empty_dossier))
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(["Objects from clipboard successfully pasted."],
                         info_messages())

        dossier_copy = self.leaf_repofolder.objectValues()[-1]
        self.assertEqual(1, len(dossier_copy.listFolderContents()))

    @browsing
    def test_object_renaming_is_not_journalized(self, browser):
        """When a object gets copied, it has to be renamed after the creation,
        to use the correct format, but this shouldn't add additional journal
        entries.
        """
        self.login(self.regular_user, browser=browser)
        create(Builder('document').within(self.empty_dossier))

        browser.open(self.empty_repofolder, view="copy_items",
                     data=self.make_path_param(self.empty_dossier))
        browser.css('#contentActionMenus a#paste').first.click()

        copy = self.empty_repofolder.objectValues()[0]

        browser.open(copy, view='tabbedview_view-journal')
        listing = browser.css('.listing').first
        self.assertEqual(
            [u'Dossier added: An empty dossier',
             u'Document added: copy of Testdokum\xe4nt',
             u'Document added: Testdokum\xe4nt',
             u'Dossier added: An empty dossier'],
            [row.get('Title') for row in listing.dicts()])

    @browsing
    def test_pasting_dossiers_into_a_branch_node_redirects_back_and_shows_statusmessage(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.leaf_repofolder,
            data=self.make_path_param(self.dossier), view="copy_items")

        browser.open(self.branch_repofolder)
        browser.click_on('Paste')

        self.assertEqual(
            ["Can't paste items, it's not allowed to add objects of this type."],
            error_messages())
        self.assertEqual(self.branch_repofolder.absolute_url(), browser.url)

    @browsing
    def test_copy_document_from_repository_into_private_dossier_fails(self, browser):  # noqa
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.dossier, view="copy_items",
            data=self.make_path_param(self.document))

        browser.open(self.private_dossier, view='paste_clipboard')
        self.assertEqual(
            ["Can't paste items, the context does not allow pasting items."],
            error_messages())

    @browsing
    def test_paste_not_available_without_copy_or_move_on_target(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view="copy_items", data=self.make_path_param(self.document))
        # A task grants us 'Contributor' on the otherwise inaccessible dossier
        browser.open(self.protected_dossier_with_task)
        expected_actions = [
            u'Add new\u2026 \u25bc',
            'Document',
            'document_with_template',
            'Task',
            'Add task from template',
            'Subdossier',
            'Participant',
            u'Actions \u25bc',
            'Cover (PDF)',
            'Export as Zip',
            'Print details (PDF)',
            'Properties',
            ]
        self.assertEqual(expected_actions, browser.css('#contentActionMenus a').text)


class TestCopyPastePermissionHandling(IntegrationTestCase):

    @browsing
    def test_preserves_role_inheritance_block_on_dossier(self, browser):
        self.login(self.administrator, browser=browser)

        self.subdossier.__ac_local_roles_block__ = True

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        subsubdossier_copy = subdossier_copy.get_subdossiers()[0].getObject()

        self.assertTrue(getattr(subdossier_copy, '__ac_local_roles_block__', False))
        self.assertFalse(getattr(subsubdossier_copy, '__ac_local_roles_block__', False))

    @browsing
    def test_preserves_role_inheritance_block_on_subdossier(self, browser):
        self.login(self.administrator, browser=browser)

        self.subsubdossier.__ac_local_roles_block__ = True

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        subsubdossier_copy = subdossier_copy.get_subdossiers()[0].getObject()

        self.assertFalse(getattr(subdossier_copy, '__ac_local_roles_block__', False))
        self.assertTrue(getattr(subsubdossier_copy, '__ac_local_roles_block__', False))

    @browsing
    def test_preserves_local_roles_from_sharing(self, browser):
        assignment_type = ASSIGNMENT_VIA_SHARING
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.subdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor']))
        manager = RoleAssignmentManager(self.subdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        manager = RoleAssignmentManager(subdossier_copy)
        assignments = manager.get_assignments_by_cause(assignment_type)

        self.assertEqual(1, len(assignments), "{} should get copied".format(assignment_class))
        assignment = assignments[0]
        expected_assignment = {'cause': assignment_type,
                               'roles': ['Reader', 'Editor', 'Contributor'],
                               'reference': None,
                               'principal': self.regular_user.id}
        self.assertEqual(expected_assignment, assignment)

    @browsing
    def test_preserves_local_roles_from_protect_dossier(self, browser):
        assignment_type = ASSIGNMENT_VIA_PROTECT_DOSSIER
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.subdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor']))
        manager = RoleAssignmentManager(self.subdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        manager = RoleAssignmentManager(subdossier_copy)
        assignments = manager.get_assignments_by_cause(assignment_type)

        self.assertEqual(1, len(assignments), "{} should get copied".format(assignment_class))
        assignment = assignments[0]
        expected_assignment = {'cause': assignment_type,
                               'roles': ['Reader', 'Editor', 'Contributor'],
                               'reference': None,
                               'principal': self.regular_user.id}
        self.assertEqual(expected_assignment, assignment)

    @browsing
    def test_preserves_local_roles_from_invitation(self, browser):
        assignment_type = ASSIGNMENT_VIA_INVITATION
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.subdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor'],
                             self.workspace))
        manager = RoleAssignmentManager(self.subdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        manager = RoleAssignmentManager(subdossier_copy)
        assignments = manager.get_assignments_by_cause(assignment_type)

        self.assertEqual(1, len(assignments), "{} should get copied".format(assignment_class))
        assignment = assignments[0]
        expected_assignment = {'cause': assignment_type,
                               'roles': ['Reader', 'Editor', 'Contributor'],
                               'reference': Oguid.for_object(self.workspace).id,
                               'principal': self.regular_user.id}
        self.assertEqual(expected_assignment, assignment)

    @browsing
    def test_does_not_preserve_local_roles_from_tasks(self, browser):
        assignment_type = ASSIGNMENT_VIA_TASK
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.subdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor'],
                             self.task))
        manager = RoleAssignmentManager(self.subdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        manager = RoleAssignmentManager(subdossier_copy)
        assignments = manager.get_assignments_by_cause(assignment_type)

        self.assertEqual(0, len(assignments),
                         "{} should not get copied".format(assignment_class))

    @browsing
    def test_does_not_preserve_local_roles_from_task_agency(self, browser):
        assignment_type = ASSIGNMENT_VIA_TASK_AGENCY
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.subdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor'],
                             self.task))
        manager = RoleAssignmentManager(self.subdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        manager = RoleAssignmentManager(subdossier_copy)
        assignments = manager.get_assignments_by_cause(assignment_type)

        self.assertEqual(0, len(assignments),
                         "{} should not get copied".format(assignment_class))

    @browsing
    def test_does_not_preserve_local_roles_from_committee_group(self, browser):
        assignment_type = ASSIGNMENT_VIA_COMMITTEE_GROUP
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.subdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor'],
                             self.committee))
        manager = RoleAssignmentManager(self.subdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")

        with self.observe_children(self. empty_repofolder) as children:
            browser.open(self.empty_repofolder)
            browser.click_on('Paste')

        self.assertEqual(1, len(children.get('added')))
        subdossier_copy = children.get('added').pop()
        manager = RoleAssignmentManager(subdossier_copy)
        assignments = manager.get_assignments_by_cause(assignment_type)

        self.assertEqual(0, len(assignments),
                         "{} should not get copied".format(assignment_class))

    def test_all_assignment_types_are_handled(self):
        assignments_dropped_when_copying = [ASSIGNMENT_VIA_TASK,
                                            ASSIGNMENT_VIA_TASK_AGENCY,
                                            ASSIGNMENT_VIA_COMMITTEE_GROUP]

        for assignment in assignments_kept_when_copying:
            assignment_class = RoleAssignment.registry[assignment]
            self.assertNotIn(assignment, assignments_dropped_when_copying,
                             "local roles for {} are not dropped anymore during "
                             "copy/paste. Please adapt this test if this change "
                             "is on purpose.".format(assignment_class))

        handled_assignments = assignments_dropped_when_copying + list(assignments_kept_when_copying)

        for key in RoleAssignment.registry:
            assignment_class = RoleAssignment.registry[assignment]
            self.assertIn(key, handled_assignments,
                          "local roles for {} are dropped during copy/paste. If this"
                          " is on purpose, please adapt this test.".format(assignment_class))

    @browsing
    def test_status_message_shown_when_local_roles_on_dossier_are_copied(self, browser):
        assignment_type = ASSIGNMENT_VIA_SHARING
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder,
                     data=self.make_path_param(self.empty_dossier), view="copy_items")
        browser.open(self.empty_repofolder)
        browser.click_on('Paste')

        self.assertItemsEqual(info_messages(),
                              ["Objects from clipboard successfully pasted."])

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor']))
        manager = RoleAssignmentManager(self.empty_dossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.leaf_repofolder,
                     data=self.make_path_param(self.empty_dossier), view="copy_items")
        browser.open(self.empty_repofolder)
        browser.click_on('Paste')

        self.assertItemsEqual(info_messages(),
                              ["Some local roles were copied with the objects",
                               "Objects from clipboard successfully pasted."])

    @browsing
    def test_status_message_shown_when_local_roles_on_subdossier_are_copied(self, browser):
        assignment_type = ASSIGNMENT_VIA_SHARING
        assignment_class = RoleAssignment.registry[assignment_type]

        self.login(self.administrator, browser=browser)

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")
        browser.open(self.empty_repofolder)
        browser.click_on('Paste')

        self.assertItemsEqual(info_messages(),
                              ["Objects from clipboard successfully pasted."])

        manager = RoleAssignmentManager(self.subsubdossier)
        manager.add_or_update_assignment(
            assignment_class(self.regular_user.id,
                             ['Reader', 'Editor', 'Contributor']))
        manager = RoleAssignmentManager(self.subsubdossier)
        assignments = manager.get_assignments_by_cause(assignment_type)
        self.assertEqual(1, len(assignments))

        browser.open(self.dossier,
                     data=self.make_path_param(self.subdossier), view="copy_items")
        browser.open(self.empty_repofolder)
        browser.click_on('Paste')

        self.assertItemsEqual(info_messages(),
                              ["Some local roles were copied with the objects",
                               "Objects from clipboard successfully pasted."])


class TestClipboardCaching(IntegrationTestCase):

    @browsing
    def test_paste_action_occurance_is_not_cached(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier)
        browser.open(self.document, view='copy_item',
                     data={'_authenticator': createToken()})

        browser.open(self.dossier)
        self.assertIn(
            'Paste',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)
