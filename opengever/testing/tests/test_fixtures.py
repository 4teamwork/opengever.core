from DateTime import DateTime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.repository.interfaces import IRepositoryFolder
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestTestingFixture(IntegrationTestCase):

    def test_administrator_user(self):
        self.assertEquals('nicole.kohler', self.administrator.getId())
        self.assertIn('Administrator', self.administrator.getRoles())

    def test_repository_root_has_static_creation_date(self):
        self.assertEquals(DateTime('2016/08/31 09:01:33 GMT+2'),
                          self.repository_root.created())

    def test_repository_root_has_static_uuid(self):
        self.assertEquals('createrepositorytree000000000001',
                          IUUID(self.repository_root))

    @browsing
    def test_repository_root_view_renders(self, browser):
        browser.login(self.administrator).open(self.repository_root)
        self.assertEquals('Ordnungssystem', plone.first_heading())

    def test_leaf_repofolder_has_no_subrepositories(self):
        self.assertFalse(
            filter(IRepositoryFolder.providedBy,
                   self.leaf_repofolder.objectValues()),
            'The "leaf repository" {!r} should not have sub'
            ' repositories as it wouldnt be a "leaf" anymore.'.format(
                self.leaf_repofolder))

    def test_branch_repofolder_has_subrepositories(self):
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
        self.assertEquals('Archiv Vertr\xc3\xa4ge', self.archive_dossier.Title())
