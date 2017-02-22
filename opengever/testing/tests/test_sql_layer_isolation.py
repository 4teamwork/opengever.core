from ftw.builder import Builder
from ftw.builder import create
from opengever.base import model
from opengever.core.testing import OPENGEVER_SQL_TEST_LAYER
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.testing import FunctionalTestCaseSQL

import transaction


class TestLayerIsolation(FunctionalTestCaseSQL):

    layer = OPENGEVER_SQL_TEST_LAYER
    is_persistent_layer = True
    use_default_fixture = True

    def test_dossier_count_first(self):
        transaction.commit()
        from plone import api
        self.assertEquals(
            2, len(api.content.find(
                portal_type='opengever.dossier.businesscasedossier')))

    def test_dossier_count_second(self):
        transaction.commit()
        from plone import api
        self.assertEquals(
            2, len(api.content.find(
                portal_type='opengever.dossier.businesscasedossier')))

    def test_admin_unit_with_commit_first(self):
        create(Builder('admin_unit').having(
            unit_id='test_unit'))
        transaction.commit()
        self.assertEquals(2, model.Session.query(AdminUnit).count())

    def test_admin_unit_with_commit_second(self):
        create(Builder('admin_unit').having(
            unit_id='test_unit'))
        transaction.commit()
        self.assertEquals(2, model.Session.query(AdminUnit).count())

    def test_admin_unit_without_commit_first(self):
        create(Builder('admin_unit').having(
            unit_id='test_unit'))
        self.assertEquals(2, model.Session.query(AdminUnit).count())

    def test_admin_unit_without_commit_second(self):
        create(Builder('admin_unit').having(
            unit_id='test_unit'))
        self.assertEquals(2, model.Session.query(AdminUnit).count())

    def test_task_first(self):
        create(Builder('task'))
        transaction.commit()

    def test_task_second(self):
        create(Builder('task'))
        transaction.commit()

    def test_global_index(self):
        create(Builder('globalindex_task').having(int_id=5321))
        transaction.commit()

    def test_global_index_consistency(self):
        create(Builder('globalindex_task').having(int_id=6321))
        transaction.commit()
