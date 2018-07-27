from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile


class TestRepositoryCreation(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryCreation, self).setUp()
        self.grant('Manager')
        applyProfile(self.portal, 'opengever.setup.tests:repositories')

    def test_repositoreis_are_created_from_setup_profiles(self):
        old_repo = self.portal['old_repo']
        new_repo = self.portal['repo']

        self.assertEqual(u'Old Repository', old_repo.Title())
        self.assertEqual(u'New Repository', new_repo.Title())

    def test_avoids_id_conflicts(self):
        self.assertEqual(
            ['fuehrung', 'fuehrung-1'], self.portal['repo'].objectIds())

    def test_set_local_roles_correctly(self):
        self.assertEqual(
            (('admin', ('Owner',)),
             (u'administratoren', ('Publisher',)),
             (u'gever eingangskorb',
              ('Contributor', 'Reviewer', 'Editor', 'Publisher')),
             (u'gever_users',
              ('Contributor', 'Reviewer', 'Publisher', 'Editor', 'Reader'))),
            self.portal['repo'].get_local_roles())
