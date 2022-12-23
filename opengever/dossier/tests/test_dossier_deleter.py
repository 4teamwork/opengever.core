from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.interfaces import IDeleter
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zExceptions import Forbidden
from zope.component import getAdapter
import transaction


class TestDossierDeleter(IntegrationTestCase):
    def test_can_delete_empty_dossier(self):
        self.login(self.manager)

        deleter = getAdapter(self.empty_dossier, IDeleter)
        with self.observe_children(self.empty_dossier.__parent__) as children:
            deleter.delete()

        self.assertEqual(1, len(children['removed']))

    def test_cannot_delete_not_empty_dossier(self):
        self.login(self.manager)
        create(Builder('dossier').titled(u'Dossier A').within(self.empty_dossier))

        deleter = getAdapter(self.empty_dossier, IDeleter)

        with self.assertRaises(Forbidden):
            deleter.delete()

    def test_cannot_delete_dossier_without_permission(self):
        self.login(self.dossier_manager)

        protector = IProtectDossier(self.empty_dossier)
        protector.dossier_manager = self.dossier_manager.getId()
        protector.reading = [self.secretariat_user.getId()]
        protector.protect()

        self.login(self.secretariat_user)
        self.assertFalse(api.user.has_permission('opengever.dossier: Delete dossier', obj=self.empty_dossier))

        deleter = getAdapter(self.empty_dossier, IDeleter)
        with self.assertRaises(Forbidden):
            deleter.delete()


class TestDossierDeleterWithTeamraum(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_cannot_delete_dossier_linked_to_a_workspace(self, browser):
        browser.login()

        with self.workspace_client_env():
            empty_dossier = create(Builder('dossier').titled(u'Dossier A').within(self.leaf_repofolder))
            manager = ILinkedWorkspaces(empty_dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            deleter = getAdapter(empty_dossier, IDeleter)

            with self.assertRaises(Forbidden):
                deleter.delete()
