from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.tests.base import OGDSTestCase


class TestInbox(OGDSTestCase):

    def setUp(self):
        super(TestInbox, self).setUp()
        self.john = create(Builder('ogds_user').id('john'))
        self.hugo = create(Builder('ogds_user').id('hugo'))
        self.peter = create(Builder('ogds_user').id('peter'))

        self.members = create(Builder('ogds_group')
                              .id('members')
                              .having(
                                  users=[self.john, self.hugo, self.peter]))

        self.inbox_members = create(Builder('ogds_group')
                                    .id('inbox_members')
                                    .having(users=[self.john, self.peter]))

        self.org_unit = create(Builder('org_unit')
                               .id('org')
                               .having(title='Unit A',
                                       users_group=self.members,
                                       inbox_group=self.inbox_members))

        self.admin_unit = create(Builder('admin_unit')
                                 .assign_org_units([self.org_unit]))

        self.inbox = self.org_unit.inbox()
        self.commit()

    def test_id_is_refixed_with_inbox_and_colon(self):
        self.assertEquals('inbox:org', self.inbox.id())

    def test_representation(self):
        self.assertEquals('<Inbox inbox:org>', repr(self.inbox))

    def test_assigned_users_list_users_from_org_units_inbox_group(self):
        self.assertEquals([self.john, self.peter],
                          self.inbox.assigned_users())
