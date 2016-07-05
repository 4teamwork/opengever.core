from opengever.core.testing import OPENGEVER_DEFAULT_CONTENT_TESTING
from opengever.testing import FunctionalTestCase


class TestDossierWithDefaultContent(FunctionalTestCase):

    layer = OPENGEVER_DEFAULT_CONTENT_TESTING

    def setUp(self):
        super(TestDossierWithDefaultContent, self).setUp()

    def test_stuff_with_content(self):
        print self.layer['le_dossier']
