from ftw.testbrowser import browsing
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.bumblebee.browser.overlay import BumblebeeBaseDocumentOverlay
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import IRefreshableLockable
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface.verify import verifyClass


class TestAdapterRegisteredProperly(IntegrationTestCase):
    """Test bumblebee overlay adapter registrations."""

    features = (
        'bumblebee',
        )

    def test_get_overlay_adapter_for_documents(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertIsInstance(adapter, BumblebeeBaseDocumentOverlay)

    def test_verify_implemented_interfaces(self):
        verifyClass(IBumblebeeOverlay, BumblebeeBaseDocumentOverlay)


class TestGetPreviewPdfUrl(IntegrationTestCase):
    """Test generating a link to the bumblebee instance."""

    features = (
        'bumblebee',
        )

    def test_returns_preview_pdf_url_as_string(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.empty_document, self.request), IBumblebeeOverlay)
        self.assertEqual(
            'http://nohost/plone/++resource++opengever.bumblebee.resources/fallback_not_digitally_available.svg',
            adapter.preview_pdf_url(),
            )


class TestGetFileSize(IntegrationTestCase):
    """Test we agree about filesize with bumblebee."""

    features = (
        'bumblebee',
        )

    def test_returns_file_size_in_kb_if_file_is_available(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(self.document.get_file().getSize() / 1024, adapter.get_file_size())

    def test_returns_none_if_no_file_is_available(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.empty_document, self.request), IBumblebeeOverlay)
        self.assertIsNone(adapter.get_file_size())


class TestGetCreator(IntegrationTestCase):
    """Test we correctly link to the document author."""

    features = (
        'bumblebee',
        )

    def test_returns_link_to_creator(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        creator_link = adapter.get_creator_link()
        self.assertIn('Ziegler Robert (robert.ziegler)', creator_link)
        self.assertIn('http://nohost/plone/@@user-details/robert.ziegler', creator_link)


class TestGetDocumentDate(IntegrationTestCase):
    """Test we correctly fetch the document date."""

    features = (
        'bumblebee',
        )

    def test_returns_localized_document_date(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(u'Jan 03, 2010', adapter.get_document_date())

    def test_returns_none_if_document_date_is_empty_string(self):
        self.login(self.regular_user)
        self.document.document_date = ''
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertIsNone(adapter.get_document_date())

    def test_returns_none_if_document_date_is_none(self):
        self.login(self.regular_user)
        self.document.document_date = None
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertIsNone(adapter.get_document_date())


class TestGetContainingDossier(IntegrationTestCase):
    """Test we correctly fetch the immediate parent dossier."""

    features = (
        'bumblebee',
        )

    def test_returns_the_containing_dossier(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(self.dossier, adapter.get_containing_dossier())


class TestGetSequenceNumber(IntegrationTestCase):
    """Test we correctly fetch the document sequence number."""

    features = (
        'bumblebee',
        )

    def test_returns_sequence_number(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(getUtility(ISequenceNumber).get_number(self.document), adapter.get_sequence_number())


class TestGetReferenceNumber(IntegrationTestCase):
    """Test we correctly fetch the document reference number."""

    features = (
        'bumblebee',
        )

    def test_returns_reference_number(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(IReferenceNumber(self.document).get_number(), adapter.get_reference_number())


class TestHasFile(IntegrationTestCase):
    """Test we correctly detect if a document has a file."""

    features = (
        'bumblebee',
        )

    def test_returns_true_if_document_has_a_file(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertTrue(adapter.has_file())

    def test_returns_false_if_document_has_no_file(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.empty_document, self.request), IBumblebeeOverlay)
        self.assertFalse(adapter.has_file())


class TestGetFile(IntegrationTestCase):
    """Test we correctly fetch the file of the document."""

    features = (
        'bumblebee',
        )

    def test_returns_none_if_document_has_no_file(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.empty_document, self.request), IBumblebeeOverlay)
        self.assertIsNone(adapter.get_file())

    def test_returns_file_if_document_has_file(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(self.document.file, adapter.get_file())


class TestRenderLockInfoViewlet(IntegrationTestCase):
    """Test we correctly render the document locking status."""

    features = (
        'bumblebee',
        )

    @browsing
    def test_returns_empty_html_if_not_locked(self, browser):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        browser.open_html(adapter.render_lock_info_viewlet())
        self.assertEqual(0, len(browser.css('.portalMessage')))

    @browsing
    def test_returns_lock_info_viewlet_if_locked(self, browser):
        self.login(self.regular_user)
        IRefreshableLockable(self.document).lock()
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        browser.open_html(adapter.render_lock_info_viewlet())
        self.assertEqual(1, len(browser.css('.portalMessage')))


class TestRenderCheckedOutViewlet(IntegrationTestCase):
    """Test we correctly render the document checkout info viewlet."""

    features = (
        'bumblebee',
        )

    @browsing
    def test_returns_empty_html_if_not_checked_out(self, browser):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertEqual(u'\n', adapter.render_checked_out_viewlet())

    @browsing
    def test_returns_lock_info_viewlet_if_checked_out(self, browser):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        browser.open_html(adapter.render_checked_out_viewlet())
        self.assertEqual(1, len(browser.css('.portalMessage')))
