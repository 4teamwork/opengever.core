from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestInbox(FunctionalTestCase):

    def setUp(self):
        super(TestInbox, self).setUp()

        self.org_unit2 = create(Builder('org_unit').id('client2')
                                .having(admin_unit=self.admin_unit))

    def test_get_responsible_org_unit_fetch_configured_org_unit(self):
        inbox = create(Builder('inbox').
                       having(responsible_org_unit='client1'))

        self.assertEqual(self.org_unit, inbox.get_responsible_org_unit())

    def test_get_responsible_org_unit_returns_none_when_no_org_unit_is_configured(self):
        inbox = create(Builder('inbox'))

        self.assertEqual(None, inbox.get_responsible_org_unit())
