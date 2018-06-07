from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.repository.indexers import sortable_title
from zope.event import notify


class TestRepositoryFolderIndexers(IntegrationTestCase):

    def test_sortable_title_index_ignores_refernce_number_length(self):
        self.login(self.secretariat_user)

        # create a 5 fold nested folder
        repofolder = reduce(
            lambda repofolder, level: create(
                Builder('repository')
                .within(repofolder)
                .having(
                    title_de=u'Vertr\xe4ge {}'.format(level),
                    title_fr=u'Contrats {}'.format(level),
                )),
            range(5),
            self.leaf_repofolder,
        )

        self.assertEquals(
            '0001.0001.0001.0001.0001.0001.0001. vertrage 0004',
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
