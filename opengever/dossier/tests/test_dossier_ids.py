from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class DossierIdsTestCase(IntegrationTestCase):

    @browsing
    def test_dossier_id_format(self, browser):
        self.login(self.regular_user)
        self.assertEquals("dossier-1", self.dossier.id)
        self.assertEquals("dossier-2", self.subdossier.id)
