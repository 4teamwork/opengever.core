from opengever.repository.browser.excel_export import generate_report
from opengever.setup.sections.xlssource import XlsSource
from opengever.testing import IntegrationTestCase
from plone import api
from tempfile import mkdtemp
from tempfile import NamedTemporaryFile
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
            u'Archival value': u'',
            u'Blocked inheritance': u'No',
            u'Classification': u'',
            u'Close dossiers local or inherited roles': self.secretariat_user.getId(),
            u'Close dossiers local roles': self.secretariat_user.getId(),
            u'Comment about archival value assessment': u'',
            u'Comment about retention period assessment': u'',
            u'Create dossiers local or inherited roles': u'fa_users\n%s' % self.archivist.getId(),
            u'Create dossiers local roles': u'fa_users\n%s' % self.archivist.getId(),
            u'Disclosure status': u'',
            u'Edit dossiers local or inherited roles': u'fa_users',
            u'Edit dossiers local roles': u'fa_users',
            u'Manage dossiers local or inherited roles': u'',
            u'Manage dossiers local roles': u'',
            u'Privacy protection': u'',
            u'Reactivate dossiers local or inherited roles': u'%s' % self.secretariat_user.getId(),
            u'Reactivate dossiers local roles': u'%s' % self.secretariat_user.getId(),
            u'Read dossiers local or inherited roles': u'fa_users',
            u'Read dossiers local roles': u'fa_users',
            u'Regular safeguard period (years)': u'',
            u'Repository number': u'',
            u'Repositoryfolder description': u'',
            u'Repositoryfolder title': u'Ordnungssystem',
            u'Repositoryfolder title (French)': u'Syst\xe8me de classement',
            u'Repositoryfolder title (German)': u'Ordnungssystem',
            u'Retention period (years)': u'',
            u'Task responsible local or inherited roles': u'',
            u'Task responsible local roles': u'',
            u'Valid from': u'',
            u'Valid until': u'',
            u'UID': u'createrepositorytree000000000001',
            u'Path': u'ordnungssystem',

        }
        self.assertEqual(imported_data[0], expected_reporoot)
        expected_repofolder = {
            '_repo_root_id': file_basename,
            '_type': u'opengever.repository.repositoryfolder',
            u'Archival value': u'not assessed',
            u'Blocked inheritance': u'No',
            u'Classification': u'unprotected',
            u'Close dossiers local or inherited roles': self.secretariat_user.getId(),
            u'Close dossiers local roles': u'',
            u'Comment about archival value assessment': u'',
            u'Comment about retention period assessment': u'',
            u'Create dossiers local or inherited roles': u'fa_users\n%s' % self.archivist.getId(),
            u'Create dossiers local roles': u'',
            u'Disclosure status': u'not assessed',
            u'Edit dossiers local or inherited roles': u'fa_users',
            u'Edit dossiers local roles': u'',
            u'Manage dossiers local or inherited roles': u'',
            u'Manage dossiers local roles': u'',
            u'Privacy protection': u'no',
            u'Reactivate dossiers local or inherited roles': u'%s' % self.secretariat_user.getId(),
            u'Reactivate dossiers local roles': u'',
            u'Read dossiers local or inherited roles': u'fa_users',
            u'Read dossiers local roles': u'',
            u'Regular safeguard period (years)': 30,
            u'Repository number': u'1',
            u'Repositoryfolder description': u'Alles zum Thema F\xfchrung.',
            u'Repositoryfolder title': u'F\xfchrung',
            u'Repositoryfolder title (French)': u'Direction',
            u'Repositoryfolder title (German)': u'F\xfchrung',
            u'Retention period (years)': 5,
            u'Task responsible local or inherited roles': u'',
            u'Task responsible local roles': u'',
            u'Valid from': u'',
            u'Valid until': u'',
            u'UID': u'createrepositorytree000000000002',
            u'Path': u'ordnungssystem/fuhrung',


        }
        self.assertEqual(imported_data[1], expected_repofolder)
