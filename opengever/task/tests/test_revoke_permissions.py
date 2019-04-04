from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.task import is_optional_task_permissions_revoking_enabled
from opengever.task.browser.revoke_permissions import RevokePermissions
from opengever.task.interfaces import ITaskSettings
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase
from plone import api
from plone.protect.utils import addTokenToUrl
from urlparse import urlparse
from z3c.relationfield.relation import RelationValue
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


class TestRevokePermissions(IntegrationTestCase):

    features = ('optional-task-permissions-revoking', )

    def test_revokes_permissions_on_task(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        storage = RoleAssignmentManager(self.subtask).storage
        self.assertEqual(
            [{'cause': 1,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.subtask),
              'principal': self.regular_user.id}],
            storage._storage())

        RevokePermissions(self.subtask, self.request)()
        self.assertEqual([], storage._storage())

    def test_revokes_permissions_on_related_items(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        storage = RoleAssignmentManager(self.document).storage
        expected_oguids = [Oguid.for_object(task).id for task in (self.task,
                           self.subtask, self.info_task, self.private_task)]
        self.assertEqual(expected_oguids,
                         [item.get('reference') for item in storage._storage()])

        RevokePermissions(self.subtask, self.request)()
        expected_oguids = [Oguid.for_object(task).id for task in
                           (self.task, self.info_task, self.private_task)]
        self.assertEqual(expected_oguids,
                         [item.get('reference') for item in storage._storage()])

    def test_revokes_permissions_on_proposal(self):
        self.login(self.dossier_responsible)

        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(self.proposaldocument))
        ITask(self.subtask).relatedItems.append(relation)
        notify(ObjectModifiedEvent(self.subtask))

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        expected_assignments = [{'cause': 1,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.subtask),
                                 'principal': self.regular_user.id}]

        document_storage = RoleAssignmentManager(self.proposaldocument).storage
        self.assertEqual(expected_assignments, document_storage._storage())

        proposal_storage = RoleAssignmentManager(self.proposal).storage
        self.assertEqual(expected_assignments, proposal_storage._storage())

        RevokePermissions(self.subtask, self.request)()
        self.assertEqual([], proposal_storage._storage())
        self.assertEqual([], document_storage._storage())

    def test_revokes_permissions_on_distinct_parent(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        storage = RoleAssignmentManager(self.dossier).storage
        self.assertIn(
            {'cause': 1,
             'roles': ['Contributor'],
             'reference': Oguid.for_object(self.subtask),
             'principal': self.regular_user.id},
            storage._storage())

        RevokePermissions(self.subtask, self.request)()
        self.assertNotIn(
            {'cause': 1,
             'roles': ['Contributor'],
             'reference': Oguid.for_object(self.subtask),
             'principal': self.regular_user.id},
            storage._storage())


class TestRevokePermissionsAuthorization(IntegrationTestCase):

    features = ('optional-task-permissions-revoking', )

    @browsing
    def test_revoke_permissions_is_only_authorized_when_feature_is_enabled(self, browser):
        self.login(self.manager, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        RevokePermissions(self.subtask, self.request)()

        self.deactivate_feature('optional-task-permissions-revoking')
        with self.assertRaises(Unauthorized):
            RevokePermissions(self.subtask, self.request)()

    @browsing
    def test_revoke_permissions_view_is_only_authorized_when_feature_is_enabled(self, browser):
        self.login(self.manager, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        url = '/'.join([self.subtask.absolute_url(), "@@revoke_permissions"])

        browser.open(addTokenToUrl(url))

        self.deactivate_feature('optional-task-permissions-revoking')
        with browser.expect_unauthorized():
            browser.open(addTokenToUrl(url))

    @browsing
    def test_revoke_permissions_is_only_authorized_for_managers_and_task_issuer(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        # dossier_responsible is subtask issuer
        RevokePermissions(self.subtask, self.request)()

        self.subtask.issuer = self.regular_user.id
        with self.assertRaises(Unauthorized):
            RevokePermissions(self.subtask, self.request)()

        self.login(self.manager, browser)
        RevokePermissions(self.subtask, self.request)()

    @browsing
    def test_revoke_permissions_view_is_only_authorized_for_managers_and_task_issuer(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        url = '/'.join([self.subtask.absolute_url(), "@@revoke_permissions"])

        # dossier_responsible is subtask issuer
        browser.open(addTokenToUrl(url))

        self.subtask.issuer = self.regular_user.id
        with browser.expect_unauthorized():
            browser.open(addTokenToUrl(url))

        api.user.grant_roles(user=self.dossier_responsible, roles=['Manager'])
        browser.open(addTokenToUrl(url))


class TestRevokePermissionsAction(IntegrationTestCase):

    features = ('optional-task-permissions-revoking', )

    @browsing
    def test_revoke_action_points_to_revoke_permissions_view(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        browser.open(self.subtask)
        revoke_action = editbar.menu_option('Actions', "Revoke permissions")
        action_url = urlparse(revoke_action.get("href"))

        self.assertEqual("/".join([self.subtask.absolute_url_path(),
                                   '@@revoke_permissions']),
                         action_url.path)

    @browsing
    def test_revoke_action_revokes_permissions_on_task(self, browser):
        self.login(self.dossier_responsible, browser)
        self.subtask.revoke_permissions = False
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        storage = RoleAssignmentManager(self.subtask).storage
        self.assertEqual(
            [{'cause': 1,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.subtask),
              'principal': self.regular_user.id}],
            storage._storage())

        browser.open(self.subtask)
        browser.click_on("Revoke permissions")
        self.assertEqual([], storage._storage())

    @browsing
    def test_revoke_action_displays_success_message(self, browser):
        # revoke action redirects to the current task and displays a success
        # message.
        self.login(self.manager, browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        browser.open(self.subtask)
        self.assertEqual([], info_messages())

        browser.click_on("Revoke permissions")
        self.assertIn('Permissions have been succesfully revoked',
                      info_messages())
        self.assertEqual(self.subtask, browser.context)


class TestRevokePermissionsFeatureDeactivated(IntegrationTestCase):

    features = ('!optional-task-permissions-revoking', )

    def test_feature_is_deactivated(self):
        self.assertFalse(is_optional_task_permissions_revoking_enabled())

    @browsing
    def test_revoke_permissions_only_shown_when_feature_is_enabled_in_add_form(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='++add++opengever.task.task')

        self.assertIsNone(browser.forms.get('form').find_field("Revoke permissions."))

        self.activate_feature('optional-task-permissions-revoking')
        browser.open(self.dossier, view='++add++opengever.task.task')
        self.assertIsNotNone(browser.forms.get('form').find_field("Revoke permissions."))
