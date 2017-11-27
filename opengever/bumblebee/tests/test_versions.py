from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import transaction


TXT_CHECKSUM = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'  # noqa


class TestBumblebeeChecksumForVersions(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestBumblebeeChecksumForVersions, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))

    @browsing
    def test_checksum_is_updated_before_storing_version(self, browser):
        content = bumblebee_asset('example.docx').bytes()
        document = create(Builder('document')
                          .within(self.dossier)
                          .attach_file_containing(
                              content,
                              u'example.docx')
                          .checked_out())

        document.update_file('foo',
                             content_type='text/plain',
                             filename=u'foo.txt')
        notify(ObjectModifiedEvent(document))
        transaction.commit()

        # checksum has not been updated
        self.assertEqual(
            DOCX_CHECKSUM, IBumblebeeDocument(document).get_checksum())

        manager = getMultiAdapter((document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkin()

        # checksum has been updated
        self.assertEqual(TXT_CHECKSUM,
                         IBumblebeeDocument(document).get_checksum())

        versioner = Versioner(document)
        history = versioner.get_history_metadata()
        self.assertEqual(2, history.getLength(countPurged=False))

        version_0 = versioner.retrieve(0)
        self.assertEqual(DOCX_CHECKSUM,
                         IBumblebeeDocument(version_0).get_checksum())

        # document checksum should be updated before storing the version
        version_1 = versioner.retrieve(1)
        self.assertEqual(TXT_CHECKSUM,
                         IBumblebeeDocument(version_1).get_checksum())
