from ftw.testbrowser import browsing
from opengever.dossier.resolve import LockingResolveManager
from opengever.officeconnector.testing import OCSolrIntegrationTestCase


class TestOfficeconnectorIsMailFileable(OCSolrIntegrationTestCase):

    features = ("officeconnector-attach", )

    @browsing
    def test_single_doc_in_open_dossier(self, browser):
        self.login(self.regular_user, browser)

        self.assertTrue(self.dossier.is_open())
        documents = [self.document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertTrue(fileable)

    @browsing
    def test_multiple_docs_in_open_dossier(self, browser):
        self.login(self.regular_user, browser)

        self.assertTrue(self.dossier.is_open())
        documents = [self.document, self.mail_eml]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertTrue(fileable)

    @browsing
    def test_single_doc_in_task_in_open_dossier(self, browser):
        self.login(self.regular_user, browser)

        self.assertTrue(self.dossier.is_open())
        documents = [self.taskdocument]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertTrue(fileable)

    @browsing
    def test_single_doc_in_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_manager = LockingResolveManager(self.resolvable_dossier)
        resolve_manager.resolve()
        self.assertFalse(self.resolvable_dossier.is_open())

        documents = [self.resolvable_document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertFalse(fileable)

    @browsing
    def test_single_doc_in_inactive_dossier(self, browser):
        self.login(self.regular_user, browser)

        self.assertFalse(self.inactive_dossier.is_open())

        documents = [self.inactive_document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertFalse(fileable)

    @browsing
    def test_multiple_docs_in_multiple_subdossiers(self, browser):
        self.login(self.regular_user, browser)

        self.assertTrue(self.dossier.is_open())
        self.assertTrue(self.subdossier.is_open())
        documents = [self.document, self.subdocument]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertFalse(fileable)

    @browsing
    def test_multiple_docs_in_multiple_maindossiers(self, browser):
        self.login(self.regular_user, browser)

        self.assertTrue(self.dossier.is_open())
        self.assertTrue(self.meeting_dossier.is_open())
        documents = [self.document, self.meeting_document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertFalse(fileable)

    @browsing
    def test_single_doc_in_inbox(self, browser):
        self.login(self.secretariat_user, browser)

        documents = [self.inbox_document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertFalse(fileable)


class TestOfficeconnectorIsMailFileableInTeamraum(OCSolrIntegrationTestCase):

    features = ('!officeconnector-checkout', 'officeconnector-attach', 'workspace')

    @browsing
    def test_single_doc_in_workspace(self, browser):
        self.login(self.workspace_member, browser)

        documents = [self.workspace_document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertTrue(fileable)

    @browsing
    def test_multiple_docs_in_multiple_workspace_folders(self, browser):
        self.login(self.workspace_member, browser)

        documents = [self.workspace_document, self.workspace_folder_document]
        fileable = self.fetch_oc_attach_is_mail_fileable(browser, documents)
        self.assertFalse(fileable)
