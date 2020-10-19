from ftw.bumblebee.interfaces import IBumblebeeUserSaltStore
from opengever.testing import IntegrationTestCase
from plone import api


class TestBumblebeeReadonlySupport(IntegrationTestCase):

    features = ('bumblebee', )

    def test_bumblebee_user_salt_created_on_login(self):
        salt_store = IBumblebeeUserSaltStore(api.portal.get())
        storage = salt_store._get_storage()

        storage.pop(self.regular_user.getId(), None)
        self.assertNotIn(self.regular_user.getId(), storage)

        self.login(self.regular_user)
        membership_tool = api.portal.get_tool('portal_membership')
        membership_tool.loginUser()

        self.assertIn(self.regular_user.getId(), storage)
