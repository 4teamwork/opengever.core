from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from opengever.bumblebee.browser.overlay import BumblebeeMailOverlay
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestAdapterRegisteredProperly(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_get_overlay_adapter_for_mails(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertIsInstance(adapter, BumblebeeMailOverlay)

    def test_verify_implemented_interfaces(self):
        verifyClass(IBumblebeeOverlay, BumblebeeMailOverlay)


class TestHasFile(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_true_if_mail_has_a_file(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertTrue(adapter.has_file())

    def test_returns_false_if_mail_has_no_file(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertFalse(adapter.has_file())


class TestGetFile(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_none_if_document_has_no_file(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_file())

    def test_returns_file_if_document_has_file(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertEqual(mail.message, adapter.get_file())


class TestGetOpenAsPdfLink(IntegrationTestCase):

    features = ('bumblebee', )

    def test_returns_none_for_unsupported_mail_conversion(self):
        self.login(self.regular_user)

        adapter = getMultiAdapter((self.mail, self.request), IBumblebeeOverlay)
        self.assertEqual(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-11/bumblebee-open-pdf?filename=die-burgschaft.pdf',
            adapter.get_open_as_pdf_url())


class TestGetCheckoutUrl(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_none_because_its_not_possible_to_checkout_emails(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_checkout_url())


class TestGetCheckinWithoutCommentUrl(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_none_because_its_not_possible_to_checkin_emails(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_checkin_without_comment_url())


class TestGetCheckinWithCommentUrl(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_returns_none_because_its_not_possible_to_checkin_emails(self):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').with_dummy_message().within(dossier))

        adapter = getMultiAdapter((mail, self.request), IBumblebeeOverlay)

        self.assertIsNone(adapter.get_checkin_with_comment_url())
