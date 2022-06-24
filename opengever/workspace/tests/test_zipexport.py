from ftw.zipexport.interfaces import IZipRepresentation
from opengever.testing import IntegrationTestCase
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
             u'/Die Buergschaft.eml',
             u'/Allgemeine Informationen',
             u'/Projekteinf\xfchrung/Go live',
             u'/Projekteinf\xfchrung/Cleanup installation',
             u'/Fix user login'],
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
