from opengever.activity import notification_center
from opengever.activity.roles import TODO_RESPONSIBLE_ROLE
from opengever.activity.roles import WORKSPACE_MEMBER_ROLE
from opengever.base.content_deleter import BaseContentDeleter
from opengever.base.interfaces import IDeleter
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from plone import api
from zExceptions import Forbidden
from zope.component import getAdapter


class TestContentDeleter(IntegrationTestCase):
    def test_can_delete_content(self):
        self.login(self.manager)

        deleter = BaseContentDeleter(self.dossier)
        with self.observe_children(self.dossier.__parent__) as children:
            deleter.delete()

        self.assertEqual(1, len(children['removed']))

    def test_verify_may_delete_raises_forbidden_without_delete_permission(self):
        self.login(self.regular_user)
        deleter = BaseContentDeleter(self.dossier)

        self.assertFalse(api.user.has_permission(deleter.permission, obj=self.dossier))
        with self.assertRaises(Forbidden):
            deleter.verify_may_delete()

        deleter.permission = 'View'
        self.assertTrue(api.user.has_permission(deleter.permission, obj=self.dossier))
        deleter.verify_may_delete()

    def test_checks_the_permission_before_delete(self):
        self.login(self.regular_user)
        deleter = BaseContentDeleter(self.dossier)

        self.assertFalse(api.user.has_permission(deleter.permission, obj=self.dossier))
        with self.assertRaises(Forbidden):
            deleter.delete()

        deleter.permission = 'View'
        self.assertTrue(api.user.has_permission(deleter.permission, obj=self.dossier))

        with self.observe_children(self.dossier.__parent__) as children:
            deleter.delete()

        self.assertEqual(1, len(children['removed']))

    def test_is_adapter(self):
        self.login(self.manager)
        adapter = getAdapter(self.repository_root, IDeleter)
        self.assertIsInstance(adapter, BaseContentDeleter)

    def test_is_delete_allowed_returns_boolean(self):
        self.login(self.regular_user)
        deleter = BaseContentDeleter(self.dossier)

        self.assertFalse(api.user.has_permission(deleter.permission, obj=self.dossier))
        self.assertFalse(deleter.is_delete_allowed())

        deleter.permission = 'View'
        self.assertTrue(api.user.has_permission(deleter.permission, obj=self.dossier))
        self.assertTrue(deleter.is_delete_allowed())

    def test_deleting_object_deletes_resource_and_subscriptions(self):
        self.activate_feature("activity")
        self.activate_feature("workspace")
        center = notification_center()
        self.login(self.workspace_admin)

        center.add_watcher_to_resource(self.workspace_document,
                                       self.workspace_member.getId(),
                                       WORKSPACE_MEMBER_ROLE)

        watcher = center.fetch_watcher(self.workspace_member.getId())
        subscriptions = watcher.subscriptions
        self.assertEqual(1, len(subscriptions))
        expected = [(WORKSPACE_MEMBER_ROLE, self.workspace_document)]
        actual = [(subscription.role, subscription.resource.oguid.resolve_object())
                  for subscription in subscriptions]
        self.assertItemsEqual(expected, actual)

        ITrasher(self.workspace_document).trash()
        IDeleter(self.workspace_document).delete()

        center.session.refresh(watcher)
        self.assertEqual([], watcher.subscriptions)
