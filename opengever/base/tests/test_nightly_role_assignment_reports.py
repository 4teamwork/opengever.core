from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.base.nightly_role_assignment_reports import NightlyRoleAssignmentReports
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.storage import STATE_IN_PROGRESS
from opengever.base.storage import STATE_READY
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import CapturingLogHandler
from plone.uuid.interfaces import IUUID
import logging


class TestNightlyRoleAssignmentReports(IntegrationTestCase):

    features = ('nightly-jobs', )

    def execute_nightly_jobs(self):

        # Create a logging setup similar to cronjob scenario
        nightly_logger = logging.getLogger('opengever.nightlyjobs')
        nightly_logger.setLevel(logging.INFO)
        nightly_log_handler = CapturingLogHandler()
        nightly_logger.addHandler(nightly_log_handler)

        nightly_job_provider = NightlyRoleAssignmentReports(
            self.portal, self.request, nightly_logger)

        jobs = list(nightly_job_provider)

        for job in jobs:
            nightly_job_provider.run_job(job, None)
        return [(r.name, r.msg) for r in nightly_log_handler.records]

    def test_nightly_role_assignment_reports(self):
        self.login(self.administrator)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update(self.meeting_user.getId(), ['Editor', 'Contributor', 'Reader'],
                              ASSIGNMENT_VIA_SHARING)
        manager = RoleAssignmentManager(self.repository_root)
        manager.add_or_update(self.meeting_user.getId(), ['Contributor', 'Reader', 'Publisher'],
                              ASSIGNMENT_VIA_SHARING)
        manager = RoleAssignmentManager(self.leaf_repofolder)
        manager.add_or_update(self.meeting_user.getId(), ['Reviewer'],
                              ASSIGNMENT_VIA_SHARING)

        storage = IRoleAssignmentReportsStorage(self.portal)

        reportid = storage.add(self.meeting_user.getId())
        report = storage.get(reportid)
        self.assertEqual(STATE_IN_PROGRESS, report['state'])
        self.assertEqual([], report['items'])

        logrecords = self.execute_nightly_jobs()
        self.assertIn(('opengever.nightlyjobs', "Complete report '{}'".format(reportid)),
                      logrecords)

        report = storage.get('report_2')
        self.assertEqual(STATE_READY, report['state'])
        self.assertEqual(
            [{'UID': IUUID(self.repository_root),
              'roles': ['Contributor', 'Reader', 'Publisher']},
             {'UID': IUUID(self.leaf_repofolder),
              'roles': ['Reviewer']},
             {'UID': IUUID(self.empty_dossier),
              'roles': ['Editor', 'Contributor', 'Reader']}], report['items'])
