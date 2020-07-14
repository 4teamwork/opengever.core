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
                u'label_archival_value_annotation': u'',
                u'label_archival_value': u'',
                u'label_classification': u'',
                u'label_custody_period': u'',
                u'label_privacy_layer': u'',
                u'label_public_trial': u'',
                u'label_retention_period_annotation': u'',
                u'label_retention_period': u'',
                u'label_valid_from': u'',
                u'label_valid_until': u'',
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
            u'label_archival_value_annotation': u'',
            u'label_archival_value': u'unchecked',
            u'label_classification': u'unprotected',
            u'label_custody_period': 30,
            u'label_privacy_layer': u'privacy_layer_no',
            u'label_public_trial': u'unchecked',
            u'label_retention_period_annotation': u'',
            u'label_retention_period': 5,
            u'label_valid_from': u'',
            u'label_valid_until': u'',
            u'Manage dossiers': u'',
            u'Reactivate dossiers': u'',
            u'Read dossiers': u'',
            u'Repository number': u'1',
            u'Repositoryfolder description': u'Alles zum Thema F\xfchrung.',
            u'Repositoryfolder title (French)': u'Direction',
            u'Repositoryfolder title (German)': u'F\xfchrung',
            }
        self.assertEqual(imported_data[1], expected_repofolder)
