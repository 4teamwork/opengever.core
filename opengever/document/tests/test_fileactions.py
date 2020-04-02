from opengever.document.fileactions import BaseDocumentFileActions
from opengever.document.fileactions import DocumentFileActions
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IFileActions
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import IntegrationTestCase
from opengever.testing.test_case import TestCase
from opengever.wopi import discovery
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi.lock import create_lock
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface.verify import verifyClass


class TestFileActionsInterface(TestCase):

    def test_base_document_file_actions_implements_ifileactions(self):
        verifyClass(IFileActions, BaseDocumentFileActions)

    def test_document_file_actions_implements_ifileactions(self):
        verifyClass(IFileActions, DocumentFileActions)


class TestIsVersionedDocument(IntegrationTestCase):
    """Test if we correctly detect if we're on a versioned document or not."""

    def test_returns_false_if_no_version_id_is_given(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(adapter.is_versioned())

    def test_returns_true_if_version_id_is_a_string(self):
        self.login(self.regular_user)
        self.request['version_id'] = '0'
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertTrue(adapter.is_versioned())

    def test_test_returns_false_if_version_id_is_no_digit(self):
        self.login(self.regular_user)
        self.request['version_id'] = u'g\xe4x'
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(adapter.is_versioned())

    def test_returns_true_if_version_id_is_a_number(self):
        self.login(self.regular_user)
        self.request['version_id'] = 123
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertTrue(adapter.is_versioned())


class TestIsVersionedMail(IntegrationTestCase):

    def test_mails_are_never_versioned(self):
        self.login(self.regular_user)
        self.request['version_id'] = '0'
        adapter = getMultiAdapter((self.mail_eml, self.request), IFileActions)
        self.assertFalse(adapter.is_versioned())


class TestOfficeOnlineEditable(IntegrationTestCase):

    def test_not_editable_by_default(self):
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(actions.is_office_online_edit_action_available())

    def test_editable_if_enabled_and_supported_document(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWOPISettings)
        settings.enabled = True
        settings.discovery_url = u'http://localhost/hosting/discovery'
        discovery._EDITABLE_EXTENSIONS = {
            'http://localhost/hosting/discovery': set(['docx', 'xlsx', 'pptx'])
        }
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertTrue(actions.is_office_online_edit_action_available())

    def test_not_editable_if_enabled_and_not_supported_document(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWOPISettings)
        settings.enabled = True
        settings.discovery_url = u'http://localhost/hosting/discovery'
        discovery._EDITABLE_EXTENSIONS = {
            'http://localhost/hosting/discovery': set(['xlsx', 'pptx'])
        }
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(actions.is_office_online_edit_action_available())

    def test_not_editable_if_checked_out_by_other(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWOPISettings)
        settings.enabled = True
        settings.discovery_url = u'http://localhost/hosting/discovery'
        discovery._EDITABLE_EXTENSIONS = {
            'http://localhost/hosting/discovery': set(['docx', 'xlsx', 'pptx'])
        }
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(actions.is_office_online_edit_action_available())

    def test_editable_if_checked_out_by_wopi(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWOPISettings)
        settings.enabled = True
        settings.discovery_url = u'http://localhost/hosting/discovery'
        discovery._EDITABLE_EXTENSIONS = {
            'http://localhost/hosting/discovery': set(['docx', 'xlsx', 'pptx'])
        }
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        create_lock(self.document, 'TOKEN')
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertTrue(actions.is_office_online_edit_action_available())


class TestOfficeConnectorActions(IntegrationTestCase):

    def set_blacklisted_ip_range(self, ip_range):
        api.portal.set_registry_record(
            'office_connector_disallowed_ip_range',
            ip_range,
            interface=IOfficeConnectorSettings)

    def test_oc_direct_checkout_action_availability(self):
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.set_blacklisted_ip_range(u'192.168.0.0/16')

        self.assertTrue(actions.is_oc_direct_checkout_action_available())

        self.request._client_addr = '127.0.0.1'
        self.assertTrue(actions.is_oc_direct_checkout_action_available())

        self.request._client_addr = '192.168.0.0'
        self.assertFalse(actions.is_oc_direct_checkout_action_available())

    def test_oc_direct_edit_action_availability(self):
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.set_blacklisted_ip_range(u'192.168.0.0/16')

        self.assertFalse(actions.is_oc_direct_edit_action_available())

        self.checkout_document(self.document)
        self.assertTrue(actions.is_oc_direct_edit_action_available())

        self.request._client_addr = '127.0.0.1'
        self.assertTrue(actions.is_oc_direct_edit_action_available())

        self.request._client_addr = '192.168.0.0'
        self.assertFalse(actions.is_oc_direct_edit_action_available())

    def test_oc_zem_checkout_action_availability(self):
        self.deactivate_feature('officeconnector-checkout')

        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.set_blacklisted_ip_range(u'192.168.0.0/16')

        self.assertTrue(actions.is_oc_zem_checkout_action_available())

        self.request._client_addr = '127.0.0.1'
        self.assertTrue(actions.is_oc_zem_checkout_action_available())

        self.request._client_addr = '192.168.0.0'
        self.assertFalse(actions.is_oc_zem_checkout_action_available())

    def test_oc_zem_edit_action_availability(self):
        self.deactivate_feature('officeconnector-checkout')

        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.set_blacklisted_ip_range(u'192.168.0.0/16')

        self.assertFalse(actions.is_oc_zem_edit_action_available())

        self.checkout_document(self.document)
        self.assertTrue(actions.is_oc_zem_edit_action_available())

        self.request._client_addr = '127.0.0.1'
        self.assertTrue(actions.is_oc_zem_edit_action_available())

        self.request._client_addr = '192.168.0.0'
        self.assertFalse(actions.is_oc_zem_edit_action_available())

    def test_oc_unsupported_file_checkout_action_availability(self):
        self.login(self.regular_user)
        actions = getMultiAdapter((self.document, self.request), IFileActions)
        self.set_blacklisted_ip_range(u'192.168.0.0/16')

        self.assertFalse(actions.is_oc_unsupported_file_checkout_action_available())

        self.document.file.contentType = u'foo/bar'
        self.assertTrue(actions.is_oc_unsupported_file_checkout_action_available())

        self.request._client_addr = '127.0.0.1'
        self.assertTrue(actions.is_oc_unsupported_file_checkout_action_available())

        self.request._client_addr = '192.168.0.0'
        self.assertFalse(actions.is_oc_unsupported_file_checkout_action_available())
