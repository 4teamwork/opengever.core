from ftw.builder import Builder
from ftw.builder import create
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.testing import IntegrationTestCase
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.base.indexes import sortable_title
from zope.event import notify


class TestRepositoryFolderIndexers(IntegrationTestCase):

    def test_sortable_title_index_accomodates_five_numbers_without_cropping(self):
        self.login(self.secretariat_user)

        title = u"".join(["a" for i in range(CONTENT_TITLE_LENGTH)])
        # create a 5 fold nested folder
        repofolder = reduce(
            lambda repofolder, level: create(
                Builder('repository')
                .within(repofolder)
                .having(
                    title_de=title,
                    title_fr=title,
                )),
            range(3),
            self.leaf_repofolder,
        )

        self.assertEquals(
            '0001.0001.0001.0001.0001. ' + title,
            sortable_title(repofolder)())

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
