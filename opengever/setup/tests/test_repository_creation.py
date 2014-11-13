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
