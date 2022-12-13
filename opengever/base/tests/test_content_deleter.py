from opengever.base.content_deleter import BaseContentDeleter
from opengever.base.interfaces import IDeleter
from opengever.testing import IntegrationTestCase
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
