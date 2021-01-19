from opengever.repository.browser.excel_export import generate_report
from opengever.setup.sections.xlssource import XlsSource
from opengever.testing import IntegrationTestCase
from plone import api
from tempfile import NamedTemporaryFile
from tempfile import mkdtemp
import os


class TestRepositoryRootExcelExport(IntegrationTestCase):

    maxDiff = None

    def test_importability_of_exported_repository_root(self):
        self.login(self.regular_user)
        report_data = generate_report(api.portal.get().REQUEST, self.repository_root)
        tempdir = mkdtemp()
        with NamedTemporaryFile(dir=tempdir, suffix='.xlsx') as tmpfile:
            tmpfile.write(report_data)
            tmpfile.flush()
            file_basename = os.path.splitext(os.path.basename(tmpfile.name))[0]
            imported_data = list(XlsSource(None, '', {'directory': tempdir, 'client_id': 'test'}, []))
        os.rmdir(tempdir)
        expected_reporoot = {
                '_repo_root_id': file_basename,
                '_type': u'opengever.repository.repositoryroot',
                u'Blocked inheritance': u'No',
                u'Close dossiers': u'jurgen.konig',
                u'Create dossiers': u'jurgen.fischer,fa_users',
                u'Edit dossiers': u'fa_users',
                u'Comment about archival value assessment': u'',
                u'Archival value': u'',
                u'Classification': u'',
                u'Regular safeguard period (years)': u'',
                u'Privacy protection': u'',
                u'Disclosure status': u'',
                u'Comment about retention period assessment': u'',
                u'Retention period (years)': u'',
                u'Valid from': u'',
                u'Valid until': u'',
                u'Manage dossiers': u'',
                u'Reactivate dossiers': u'jurgen.konig',
                u'Read dossiers': u'fa_users',
                u'Repository number': u'',
                u'Repositoryfolder description': u'',
                u'Repositoryfolder title (French)': u'Syst\xe8me de classement',
                u'Repositoryfolder title (German)': u'Ordnungssystem',
                }
        self.assertEqual(imported_data[0], expected_reporoot)
        expected_repofolder = {
            '_repo_root_id': file_basename,
            '_type': u'opengever.repository.repositoryfolder',
            u'Blocked inheritance': u'No',
            u'Close dossiers': u'',
            u'Create dossiers': u'',
            u'Edit dossiers': u'',
            u'Comment about archival value assessment': u'',
            u'Archival value': u'not assessed',
            u'Classification': u'unprotected',
            u'Regular safeguard period (years)': 30,
            u'Privacy protection': u'no',
            u'Disclosure status': u'not assessed',
            u'Comment about retention period assessment': u'',
            u'Retention period (years)': 5,
            u'Valid from': u'',
            u'Valid until': u'',
            u'Manage dossiers': u'',
            u'Reactivate dossiers': u'',
            u'Read dossiers': u'',
            u'Repository number': u'1',
            u'Repositoryfolder description': u'Alles zum Thema F\xfchrung.',
            u'Repositoryfolder title (French)': u'Direction',
            u'Repositoryfolder title (German)': u'F\xfchrung',
            }
        self.assertEqual(imported_data[1], expected_repofolder)
