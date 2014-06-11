from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain


class TestClientIdIndexer(FunctionalTestCase):

    def setUp(self):
        create(Builder('fixture').with_all_unit_setup())

    def test_client_id_is_none_for_a_document_in_a_dossier(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        self.assertEquals(None, obj2brain(document).client_id)
        self.assertEquals('', index_data_for(document).get('client_id'))

    def test_client_id_is_current_org_unit_id_for_a_document_in_a_inbox(self):
        inbox = create(Builder('inbox'))
        document = create(Builder('document').within(inbox))

        self.assertEquals('client1', obj2brain(document).client_id)
        self.assertEquals(['client1'], index_data_for(document).get('client_id'))

    def test_client_id_is_current_org_unit_id_for_a_document_in_a_inbox(self):
        yearfolder = create(Builder('yearfolder'))
        document = create(Builder('document').within(yearfolder))

        self.assertEquals('client1', obj2brain(document).client_id)
        self.assertEquals(['client1'], index_data_for(document).get('client_id'))
