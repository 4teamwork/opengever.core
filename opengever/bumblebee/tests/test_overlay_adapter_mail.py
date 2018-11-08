from ftw.mail.mail import IMail
from opengever.bumblebee.browser.overlay import BumblebeeMailOverlay
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestAdapterRegisteredProperly(IntegrationTestCase):

    features = ('bumblebee', )

    def test_get_overlay_adapter_for_mails(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertIsInstance(adapter, BumblebeeMailOverlay)

    def test_verify_implemented_interfaces(self):
        verifyClass(IBumblebeeOverlay, BumblebeeMailOverlay)


class TestHasFile(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_true_if_mail_has_a_file(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertTrue(adapter.has_file())

    def test_returns_false_if_mail_has_no_file(self):
        self.login(self.regular_user)
        IMail(self.mail_eml).message = None
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertFalse(adapter.has_file())


class TestGetFile(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_if_document_has_no_file(self):
        self.login(self.regular_user)
        IMail(self.mail_eml).message = None
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_file())

    def test_returns_file_if_document_has_file(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertEqual(self.mail_eml.message, adapter.get_file())


class TestGetOpenAsPdfLink(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_for_unsupported_mail_conversion(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        expected_url = (
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-24'
            '/bumblebee-open-pdf?filename=Die%20Buergschaft.pdf'
            )

        self.assertEqual(expected_url, adapter.get_open_as_pdf_url())

    def test_handles_non_ascii_characters_in_filename(self):
        self.login(self.regular_user)
        IMail(self.mail_eml).message.filename = u'GEVER - \xdcbernahme.msg'
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        expected_url = (
            u'http://nohost/plone/ordnungssystem/fuhrung'
            u'/vertrage-und-vereinbarungen/dossier-1/document-24'
            u'/bumblebee-open-pdf?filename=GEVER%20-%20%C3%9Cbernahme.pdf'
            )

        self.assertEqual(expected_url, adapter.get_open_as_pdf_url())


class TestGetCheckoutUrl(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_because_its_not_possible_to_checkout_emails(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_checkout_url())


class TestGetCheckinWithoutCommentUrl(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_because_its_not_possible_to_checkin_emails(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_checkin_without_comment_url())


class TestGetCheckinWithCommentUrl(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_because_its_not_possible_to_checkin_emails(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.mail_eml, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_checkin_with_comment_url())
