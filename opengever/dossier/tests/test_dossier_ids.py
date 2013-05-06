from opengever.dossier.testing import OPENGEVER_DOSSIER_FUNCTIONAL_TESTING
from opengever.testing import FunctionalTestCase
from plone.dexterity.utils import createContentInContainer


class DossierIdsTestCase(FunctionalTestCase):

    layer = OPENGEVER_DOSSIER_FUNCTIONAL_TESTING

    def setUp(self):
        super(DossierIdsTestCase, self).setUp()
        self.grant('Contributor')

    def test_dossier_id_format(self):
        dossier1 = self.create_dossier()
        dossier2 = self.create_dossier()
        self.assertEquals("dossier-1", dossier1.id)
        self.assertEquals("dossier-2", dossier2.id)

    def create_dossier(self):
        return createContentInContainer(self.portal,
                                        'opengever.dossier.businesscasedossier')
