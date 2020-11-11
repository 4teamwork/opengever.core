from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.model import Committee
from opengever.testing import FunctionalTestCase


class TestCommitteeQuery(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeQuery, self).setUp()

        self.local_admin_unit = create(
            Builder('admin_unit')
            .having(unit_id=u'local')
            .as_current_admin_unit()
        )
        self.local_committee = create(
            Builder('committee_model')
            .having(int_id=5678, admin_unit_id=u'local', title=u'Local')
        )
        self.remote_admin_unit = create(
            Builder('admin_unit')
            .having(unit_id=u'remote')
        )
        self.remote_committee = create(
            Builder('committee_model')
            .having(int_id=1234, admin_unit_id=u'remote', title=u'Remote')
        )

    def test_committee_query_limits_by_current_admin_unit(self):
        self.assertEqual(
            self.local_committee,
            Committee.query.by_current_admin_unit().one()
        )
