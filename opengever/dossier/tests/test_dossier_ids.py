from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing

class DossierIdsTestCase(IntegrationTestCase):

    @browsing
    def test_dossier_id_format(self, browser):
        self.login(self.regular_user)
        self.assertEquals("dossier-1", self.dossier.id)
        self.assertEquals("dossier-2", self.subdossier.id)
