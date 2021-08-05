from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedDocuments


class TestListLinkedDocumentUIDsFromWorkspace(IntegrationTestCase):

    @browsing
    def test_returns_a_dict_with_a_list_of_gever_uids(self, browser):
        self.login(self.workspace_guest, browser=browser)

        ILinkedDocuments(self.workspace_document).link_gever_document('GEVER_UID_1')
        ILinkedDocuments(self.workspace_mail).link_gever_document('GEVER_UID_2')

        url = '{}/@list-linked-gever-documents-uids'.format(
            self.workspace.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEquals(
            {'gever_doc_uids': ['GEVER_UID_1', 'GEVER_UID_2']},
            browser.json)

    @browsing
    def test_query_is_unrestricted(self, browser):
        self.login(self.workspace_admin, browser=browser)

        protected_document = create(Builder('document')
                                    .within(self.workspace_folder))
        ILinkedDocuments(protected_document).link_gever_document('GEVER_UID_1')
        self.workspace_folder.__ac_local_roles_block__ = True
        self.workspace_folder.reindexObjectSecurity()
        self.workspace_folder.reindexObject(idxs=['blocked_local_roles'])

        self.login(self.workspace_guest, browser=browser)
        url = '{}/@list-linked-gever-documents-uids'.format(
            self.workspace.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEquals(
            {'gever_doc_uids': ['GEVER_UID_1']},
            browser.json)
