from opengever.testing import IntegrationTestCase
from zope.event import notify
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked


class TestRepositoryFolderIndexers(IntegrationTestCase):

    def test_blocked_local_roles(self):
        self.login(self.regular_user)
        self.leaf_repofolder.reindexObject()

        self.assert_index_value(False, 'blocked_local_roles', self.leaf_repofolder)

        self.leaf_repofolder.__ac_local_roles_block__ = True
        self.leaf_repofolder.reindexObject()

        self.assert_index_value(True, 'blocked_local_roles', self.leaf_repofolder)

        self.leaf_repofolder.__ac_local_roles_block__ = False
        notify(LocalRolesAcquisitionActivated(self.leaf_repofolder, ))

        self.assert_index_value(False, 'blocked_local_roles', self.leaf_repofolder)

        self.leaf_repofolder.__ac_local_roles_block__ = True
        notify(LocalRolesAcquisitionBlocked(self.leaf_repofolder, ))

        self.assert_index_value(True, 'blocked_local_roles', self.leaf_repofolder)
