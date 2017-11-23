from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.bumblebee.tests.helpers import download_token_for
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID
from Products.Archetypes.event import ObjectEditedEvent
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import transaction


class TestBumblebeeDownloadView(FunctionalTestCase):
    """Test the bumblebee_download view.

    Duplicates (and uses docuemnt builder in) methods from ftw.bumblebee tests
    since we still want the original behaviour as long as the document is not
    checked out.

    """
    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestBumblebeeDownloadView, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))

    @browsing
    def test_download_last_version_for_checked_out_docs(self, browser):
        content = bumblebee_asset('example.docx').bytes()
        document = create(Builder('document')
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

        # download first history version
        browser.open(view='bumblebee_download',
                     data={'token': download_token_for(document),
                           'uuid': IUUID(document),
                           'checksum': DOCX_CHECKSUM})
        self.assertEqual(content, browser.contents)
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            browser.headers.get('Content-Type'))

    @browsing
    def test_download_newest_version(self, browser):
        doc = create(Builder('document')
                     .attach_file_containing(u'The Content', name=u'file.pdf')
                     .within(self.dossier))

        browser.open(view='bumblebee_download',
                     data={'token': download_token_for(doc),
                           'uuid': IUUID(doc),
                           'checksum': IBumblebeeDocument(doc).get_checksum()})
        self.assertEqual('The Content', browser.contents)
        self.assertEqual('application/pdf',
                         browser.headers.get('Content-Type'))

    @browsing
    def test_parameters_required(self, browser):
        with browser.expect_http_error(reason='Bad Request'):
            browser.open(view='bumblebee_download')

    @browsing
    def test_download_version_after_a_change(self, browser):
        doc = create(Builder('document')
                     .attach_file_containing(u'text', name=u'file.pdf')
                     .within(self.dossier))
        initial_checksum = IBumblebeeDocument(doc).get_checksum()

        # We store these parameters as they were sent to bumblebee with /store
        params = {'token': download_token_for(doc),
                  'uuid': IUUID(doc),
                  'checksum': initial_checksum}

        # then the file changes, a new version is created.
        doc.file = NamedBlobFile(data='some other text', filename=u'foo.pdf')
        doc.setModificationDate(datetime.now())
        notify(ObjectEditedEvent(doc))
        transaction.commit()

        self.assertNotEqual(
            initial_checksum, IBumblebeeDocument(doc).get_checksum(),
            'Expected the checksum to have changed when object was updated.')

        # when accessing the previous version, the LRU may trigger a refresh
        # and may want to download the file again.
        browser.open(view='bumblebee_download', data=params)
        self.assertEqual('text', browser.contents)
        self.assertEqual('application/pdf',
                         browser.headers.get('Content-Type'))

    @browsing
    def test_notfound_when_we_have_no_version_with_this_checksum(self, browser):
        doc = create(Builder('document')
                     .attach_file_containing(u'The Content', name=u'file.pdf')
                     .within(self.dossier))

        with browser.expect_http_error(reason='Not Found'):
            browser.open(view='bumblebee_download',
                         data={'token': download_token_for(doc),
                               'uuid': IUUID(doc),
                               'checksum': 'wrong-checksum'})
