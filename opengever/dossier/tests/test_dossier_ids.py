from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class DossierIdsTestCase(FunctionalTestCase):

    def setUp(self):
        super(DossierIdsTestCase, self).setUp()
        self.grant('Contributor')

    def test_dossier_id_format(self):
        dossier1 = create(Builder("dossier"))
        dossier2 = create(Builder("dossier"))

        self.assertEquals("dossier-1", dossier1.id)
        self.assertEquals("dossier-2", dossier2.id)
