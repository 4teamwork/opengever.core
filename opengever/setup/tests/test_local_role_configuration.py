from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile


class TestLocalRoleConfiguration(FunctionalTestCase):

    def setUp(self):
        super(TestLocalRoleConfiguration, self).setUp()
        self.grant('Manager')
        self.folder = create(Builder('folder').with_id('folder'))
        applyProfile(self.portal, 'opengever.setup.tests:localroles')

    def test_local_roles_are_configured(self):
        self.assertTrue(self.folder.has_local_roles())
        self.assertSequenceEqual(
            ('Contributor', 'Editor', 'Reader'),
            self.folder.get_local_roles_for_userid('somebody'))
