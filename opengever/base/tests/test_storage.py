from datetime import datetime
from ftw.testing import freeze
from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.base.storage import PRINCIPAL_TYPE_USER
from opengever.base.storage import STATE_IN_PROGRESS
from opengever.base.storage import STATE_READY
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestRoleAssignmentReportsStorage(IntegrationTestCase):
    maxDiff = None

    def setUp(self):
        super(TestRoleAssignmentReportsStorage, self).setUp()
        self.storage = IRoleAssignmentReportsStorage(self.portal)
        self.login(self.administrator.getId())

    def test_list_reports(self):
        self.assertEqual(
            [{'items': [],
              'modified': u'2016-08-31T20:01:33+00:00',
              'principal_type': PRINCIPAL_TYPE_USER,
              'principalid': self.regular_user.getId(),
              'reportid': 'report_1',
              'state': STATE_IN_PROGRESS},
             {'items': [{'UID': IUUID(self.repository_root),
                         'roles': ['Contributor']},
                        {'UID': IUUID(self.empty_repofolder),
                         'roles': ['Contributor', 'Publisher']},
                        {'UID': IUUID(self.subsubdossier),
                         'roles': ['Reader', 'Editor', 'Reviewer']}],
              'modified': u'2016-08-31T20:01:33+00:00',
              'principal_type': PRINCIPAL_TYPE_USER,
              'principalid': self.archivist.getId(),
              'reportid': 'report_0',
              'state': STATE_READY}], self.storage.list())

    def test_get_report(self):
        report = self.storage.get('report_0')
        self.assertEqual(
            {'items': [{'UID': IUUID(self.repository_root),
                        'roles': ['Contributor']},
                       {'UID': IUUID(self.empty_repofolder),
                        'roles': ['Contributor', 'Publisher']},
                       {'UID': IUUID(self.subsubdossier),
                        'roles': ['Reader', 'Editor', 'Reviewer']}],
             'modified': u'2016-08-31T20:01:33+00:00',
             'principal_type': PRINCIPAL_TYPE_USER,
             'principalid': self.archivist.getId(),
             'reportid': 'report_0',
             'state': STATE_READY}, report)

        report = self.storage.get('report_1')
        self.assertEqual(
            {'items': [],
             'modified': u'2016-08-31T20:01:33+00:00',
             'principal_type': PRINCIPAL_TYPE_USER,
             'principalid': self.regular_user.getId(),
             'reportid': 'report_1',
             'state': STATE_IN_PROGRESS}, report)

    def test_delete_report(self):
        self.storage.get('report_1')
        self.storage.delete('report_1')

        with self.assertRaises(KeyError):
            self.storage.get('report_1')

    def test_add_report(self):
        with freeze(datetime(2018, 4, 30)):
            reportid = self.storage.add(self.administrator.getId())

        self.assertEqual(
            {'items': [],
             'state': STATE_IN_PROGRESS,
             'modified': '2018-04-30T00:00:00+00:00',
             'principal_type': PRINCIPAL_TYPE_USER,
             'principalid': self.administrator.getId(),
             'reportid': reportid}, self.storage.get(reportid))

    def test_add_two_reports_for_the_same_principal(self):
        with freeze(datetime(2018, 4, 30)) as clock:
            reportid_1 = self.storage.add(self.administrator.getId())
            clock.forward(days=2)
            reportid_2 = self.storage.add(self.administrator.getId())

        self.assertEqual(
            [{'items': [],
              'modified': u'2018-05-02T00:00:00+00:00',
              'principal_type': PRINCIPAL_TYPE_USER,
              'principalid': self.administrator.getId(),
              'reportid': reportid_2,
              'state': STATE_IN_PROGRESS},
             {'items': [],
              'modified': u'2018-04-30T00:00:00+00:00',
              'principal_type': PRINCIPAL_TYPE_USER,
              'principalid': self.administrator.getId(),
              'reportid': reportid_1,
              'state': STATE_IN_PROGRESS}], self.storage.list()[:2])

    def test_update_report(self):
        with freeze(datetime(2018, 4, 30)):
            self.storage.update('report_1', {
                'state': STATE_READY,
                'items': [{
                    'UID': IUUID(self.repository_root),
                    'roles': ['Contributor']}]})

        self.assertEqual(
            {'items': [{'UID': IUUID(self.repository_root),
                        'roles': ['Contributor']}],
             'modified': u'2018-04-30T00:00:00+00:00',
             'principal_type': PRINCIPAL_TYPE_USER,
             'principalid': self.regular_user.getId(),
             'reportid': 'report_1',
             'state': STATE_READY}, self.storage.get('report_1'))

    def test_new_reportid_is_based_on_a_counter_in_storage(self):
        self.storage._storage['next_id'] = 42
        self.storage.add(self.administrator.getId())
        self.assertEqual(43, self.storage._storage['next_id'])
