from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create


class DossierIdsTestCase(FunctionalTestCase):

    def setUp(self):
        super(DossierIdsTestCase, self).setUp()
        self.grant('Contributor')

    def test_dossier_id_format(self):
        dossier1 = create(Builder("dossier"))
        dossier2 = create(Builder("dossier"))

        self.assertEquals("dossier-1", dossier1.id)
        self.assertEquals("dossier-2", dossier2.id)
