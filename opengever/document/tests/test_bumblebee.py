from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.bumblebee import utils as bumblebee_utils


class TestBumblebee(FunctionalTestCase):
    """Test integration of ftw.bumblebee."""

    def setUp(self):
        super(TestBumblebee, self).setUp()

        self.document = create(Builder('document')
                               .attach_file_containing(
                                   bumblebee_asset('example.docx').bytes(),
                                   u'example.docx'))

    def test_bumblebee_checksum_is_calculated_for_opengever_docs(self):
        self.assertEquals(
            DOCX_CHECKSUM,
            bumblebee_utils.get_document_checksum(self.document))
