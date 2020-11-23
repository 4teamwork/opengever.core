from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.zipfilestream import ZipFile
from opengever.testing import IntegrationTestCase
from opengever.testing import set_preferred_language
from StringIO import StringIO
from zope.component import getMultiAdapter


class TestTaskZipExport(IntegrationTestCase):

    def test_task_zip_export_prefix_de(self):
        set_preferred_language(self.request, 'de-ch')
        self.login(self.dossier_responsible)
        task_zip_adapter = getMultiAdapter((self.dossier, self.request), interface=IZipRepresentation)
        paths = [
            path_and_file[0]
            for path_and_file in task_zip_adapter.get_files()
            ]
        self.assertIn(
            u'/Aufgabe - Vertragsentwurf \xdcberpr\xfcfen/Feedback zum Vertragsentwurf.docx',
            paths)

    def test_task_zip_export_prefix_fr(self):
        set_preferred_language(self.request, 'fr-ch')
        self.login(self.dossier_responsible)
        task_zip_adapter = getMultiAdapter((self.dossier, self.request), interface=IZipRepresentation)
        paths = [
            path_and_file[0]
            for path_and_file in task_zip_adapter.get_files()
            ]
        self.assertIn(
            u'/T\xe2che - Vertragsentwurf \xdcberpr\xfcfen/Feedback zum Vertragsentwurf.docx',
            paths)

    @browsing
    def test_empty_tasks_are_not_exported(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        create(Builder('task')
               .within(self.subsubdossier)
               .titled(u'I am empty and not in the zip export')
               .having(responsible_client='fa',
                       responsible=self.dossier_responsible.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction')
               .in_progress())

        browser.open(self.subsubdossier, view='zip_export')
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertEqual(
            [self.subsubdocument.get_filename()],
            zip_file.namelist()
        )

    @browsing
    def test_nested_empty_tasks_are_not_exported(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        task = create(Builder('task')
               .within(self.subsubdossier)
               .titled(u'I am empty and not in the zip export')
               .having(responsible_client='fa',
                       responsible=self.dossier_responsible.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction')
               .in_progress())
        create(Builder('task')
               .within(task)
               .titled(u'I nested but also empty and not in the zip export')
               .having(responsible_client='fa',
                       responsible=self.dossier_responsible.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction')
               .in_progress())

        browser.open(self.subsubdossier, view='zip_export')
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertEqual(
            [self.subsubdocument.get_filename()],
            zip_file.namelist()
        )

    @browsing
    def test_tasks_with_documents_are_exported(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        task = create(Builder('task')
               .within(self.subsubdossier)
               .titled(u'I have a document and am in the zip export')
               .having(responsible_client='fa',
                       responsible=self.dossier_responsible.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction')
               .in_progress())
        create(
            Builder('document')
            .within(task)
            .titled(u'Feedback zum Vertragsentwurf')
            .attach_file_containing(
                'Feedback text',
                u'vertr\xe4g sentwurf.docx',
            ))

        browser.open(self.subsubdossier, view='zip_export')
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertEqual(
            [self.subsubdocument.get_filename(),
             u'Task - I have a document and am in the zip export/Feedback '
              'zum Vertragsentwurf.docx'],
            zip_file.namelist()
        )
