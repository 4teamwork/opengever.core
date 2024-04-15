from ftw.testbrowser import browsing
from ftw.zipexport.interfaces import IZipRepresentation
from opengever.testing import IntegrationTestCase
from zExceptions import Forbidden
from zope.component import getMultiAdapter


class TestWorkspaceZipExport(IntegrationTestCase):

    def test_workspace_zip_export(self):
        self.login(self.workspace_member)
        zip_adapter = getMultiAdapter((self.workspace, self.request),
                                      interface=IZipRepresentation)
        paths = [
            path_and_file[0]
            for path_and_file in zip_adapter.get_files()
        ]

        self.assertEqual(
            [u'/WS F\xc3lder/Ordnerdokument.txt',
             u'/Teamraumdokument.txt',
             u'/Die Buergschaft.eml'],
            paths)

    def test_workspacefolder_zip_export(self):
        self.login(self.workspace_member)
        zip_adapter = getMultiAdapter((self.workspace_folder, self.request),
                                      interface=IZipRepresentation)
        paths = [
            path_and_file[0]
            for path_and_file in zip_adapter.get_files()
        ]

        self.assertEqual([u'/Ordnerdokument.txt'], paths)

    @browsing
    def test_guest_cannot_zip_export_from_restricted_workspace(self, browser):
        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.login(self.workspace_guest, browser)
        browser.exception_bubbling = True
        with self.assertRaises(Forbidden):
            browser.open(self.workspace, view='zip_export')

    @browsing
    def test_guest_can_zip_export_from_unrestricted_workspace(self, browser):
        self.login(self.workspace_guest, browser)
        browser.open(self.workspace, view='zip_export')
        self.assertEqual(browser.contents[:4], 'PK\x03\x04')

    @browsing
    def test_guest_cannot_zip_selected_from_restricted_workspace(self, browser):
        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.login(self.workspace_guest, browser)
        docs = [self.workspace_document]
        data = self.make_path_param(*docs)
        browser.exception_bubbling = True
        with self.assertRaises(Forbidden):
            browser.open(self.workspace, view='zip_selected', data=data)

    @browsing
    def test_guest_can_zip_select_from_unrestricted_workspace(self, browser):
        self.login(self.workspace_guest, browser)
        docs = [self.workspace_document]
        data = self.make_path_param(*docs)
        browser.open(self.workspace, view='zip_selected', data=data)
        self.assertEqual(browser.contents[:4], 'PK\x03\x04')
