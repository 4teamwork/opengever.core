from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER
from opengever.officeatwork.ocmfile import OCMFile
from opengever.testing import FunctionalTestCase


class TestOcmFile(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER

    def setUp(self):
        super(TestOcmFile, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .within(self.dossier)
                               .as_shadow_document())

    def test_create_ocm_file_for_document(self):
        ocmfile = OCMFile.for_officeatwork(self.document)
        self.assertEqual(
            {'action': 'officeatwork',
             'cookie': '',
             'document': {
                'metadata': {},
                'title': u'Testdokum\xe4nt',
                'url': 'http://nohost/plone/dossier-1/document-1'}},
            ocmfile.get_data())
