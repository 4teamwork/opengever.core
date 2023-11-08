from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater
from opengever.nightlyjobs.runner import NightlyJobRunner
from opengever.testing import IntegrationTestCase


class TestNightlyJobsStats(IntegrationTestCase):

    @browsing
    def test_nightly_jobs_stats(self, browser):
        self.login(self.manager, browser)

        with NightlyWorkflowSecurityUpdater(reindex_security=False) as updater:
            updater.update(['opengever_mail_workflow', 'opengever_repositoryroot_workflow'])
        browser.open(self.portal, view='nightly-jobs-stats')

        self.assertEqual('Nightly status: unhealthy\n'
                         'Last nightly run: never\n\n'
                         'Nightly job counts:\n'
                         'maintenance-jobs: 4\n'
                         'create-dossier-journal-pdf: 0\n'
                         'deliver-sip-packages: 0\n'
                         'update-disposition-permissions: 2\n'
                         'execute-after-resolve-jobs: 0\n'
                         'complete-role-assignment-reports: 1', browser.contents)

        with freeze(datetime(2019, 12, 31, 17, 45)) as clock:
            runner = NightlyJobRunner(force_execution=True)
            runner.execute_pending_jobs()
            clock.forward(hours=5)
            browser.open(self.portal, view='nightly-jobs-stats')

        self.assertEqual('Nightly status: healthy\n'
                         'Last nightly run: 2019-12-31T17:45:00\n\n'
                         'Nightly job counts:\n'
                         'maintenance-jobs: 0\n'
                         'create-dossier-journal-pdf: 0\n'
                         'deliver-sip-packages: 0\n'
                         'update-disposition-permissions: 0\n'
                         'execute-after-resolve-jobs: 0\n'
                         'complete-role-assignment-reports: 0', browser.contents)
