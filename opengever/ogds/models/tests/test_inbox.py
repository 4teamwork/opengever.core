from opengever.ogds.models.tests.base import OGDSTestCase


class TestInbox(OGDSTestCase):
    def test_id_is_refixed_with_inbox_and_colon(self):
        self.assertEquals('inbox:unita', self.inbox.id())

    def test_representation(self):
        self.assertEquals('<Inbox inbox:unita>', repr(self.inbox))

    def test_assigned_users_list_users_from_org_units_inbox_group(self):
        self.assertEquals([self.john, self.peter], self.inbox.assigned_users())
