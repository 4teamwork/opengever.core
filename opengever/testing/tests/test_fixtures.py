from DateTime import DateTime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.ogds.models.user_settings import UserSettings
from opengever.repository.interfaces import IRepositoryFolder
from opengever.testing import IntegrationTestCase
from plone import api
from plone.uuid.interfaces import IUUID
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestTestingFixture(IntegrationTestCase):

    def test_administrator_user(self):
        self.login(self.regular_user)
        self.assertEquals('nicole.kohler', self.administrator.getId())
        self.assertIn('Administrator', self.administrator.getRoles())

    def test_users_have_seen_all_tours(self):
        self.login(self.regular_user)
        self.assertEqual(
            ["*"],
            UserSettings.get_setting_for_user(api.user.get_current().getId(), 'seen_tours'))

    def test_repository_root_has_static_creation_date(self):
        self.login(self.regular_user)
        self.assertEquals(DateTime('2016/08/31 09:01:33 GMT+2'),
                          self.repository_root.created())

    def test_repository_root_has_static_intid(self):
        self.login(self.regular_user)
        self.assertEquals(1007013300,
                          getUtility(IIntIds).getId(self.repository_root))

    def test_dossier_has_static_intid(self):
        self.login(self.regular_user)
        self.assertEquals(1014013300,
                          getUtility(IIntIds).getId(self.dossier))

    def test_repository_root_has_static_uuid(self):
        self.login(self.regular_user)
        self.assertEquals('createrepositorytree000000000001',
                          IUUID(self.repository_root))

    def test_dossier_manager_user(self):
        self.login(self.dossier_manager)
        self.assertEquals('faivel.fruhling', self.dossier_manager.getId())
        self.assertListEqual(['Member', 'Authenticated'],
                             self.dossier_manager.getRoles())

        self.assertIn('DossierManager',
                      api.user.get_roles(user=self.dossier_manager,
                                         obj=self.branch_repofolder))

        # Role should be inherited by sub-objects
        self.assertIn('DossierManager',
                      api.user.get_roles(user=self.dossier_manager,
                                         obj=self.dossier))

        # User should not have the dossier-manager role on the empty repofolder
        self.assertNotIn('DossierManager',
                         api.user.get_roles(user=self.dossier_manager,
                                            obj=self.empty_repofolder))

    @browsing
    def test_repository_root_view_renders(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root)
        self.assertEquals('Ordnungssystem', plone.first_heading())

    def test_leaf_repofolder_has_no_subrepositories(self):
        self.login(self.regular_user)
        self.assertFalse(
            filter(IRepositoryFolder.providedBy,
                   self.leaf_repofolder.objectValues()),
            'The "leaf repository" {!r} should not have sub'
            ' repositories as it wouldnt be a "leaf" anymore.'.format(
                self.leaf_repofolder))

    def test_branch_repofolder_has_subrepositories(self):
        self.login(self.regular_user)
        self.assertTrue(
            filter(IRepositoryFolder.providedBy,
                   self.branch_repofolder.objectValues()),
            'The "branch repository folder" {!r} must have sub'
            ' repositories as it wouldnt be a "branch" anymore.'.format(
                self.branch_repofolder))

    def test_dossiers(self):
        """This test makes sure that the objects are not acceidentally
        scrambled up when fiddling with the fixture.
        It also tests that the content attributes are available on the
        test case.
        """
        self.login(self.dossier_responsible)
        self.assertEquals('Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
                          self.dossier.Title())
        self.assertEquals('2016', self.subdossier.Title())
        self.assertEquals('Abgeschlossene Vertr\xc3\xa4ge', self.expired_dossier.Title())
