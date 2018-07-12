from ftw.zipexport.interfaces import IZipRepresentation
from opengever.testing import IntegrationTestCase
from opengever.testing import set_preferred_language
from zope.component import getMultiAdapter


class TestTaskZipExport(IntegrationTestCase):

    def test_task_zip_export_prefix_de(self):
        set_preferred_language(self.request, 'de-ch')
        self.login(self.dossier_responsible)
        task_zip_adapter = getMultiAdapter((self.task, self.request), interface=IZipRepresentation)
        paths = [
            path_and_file[0]
            for path_and_file in task_zip_adapter.get_files()
            ]
        expected_paths = [
            u'/Aufgabe - Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'/Feedback zum Vertragsentwurf.docx',
            ]
        self.assertEqual(paths, expected_paths)

    def test_task_zip_export_prefix_fr(self):
        set_preferred_language(self.request, 'fr-ch')
        self.login(self.dossier_responsible)
        task_zip_adapter = getMultiAdapter((self.task, self.request), interface=IZipRepresentation)
        paths = [
            path_and_file[0]
            for path_and_file in task_zip_adapter.get_files()
            ]
        expected_paths = [
            u'/T\xe2che - Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'/Feedback zum Vertragsentwurf.docx',
            ]
        self.assertEqual(paths, expected_paths)
