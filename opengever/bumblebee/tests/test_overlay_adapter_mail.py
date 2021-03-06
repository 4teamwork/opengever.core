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
