from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.ogds.base.actor import Actor


class TestResolveOGUIDView(FunctionalTestCase):

    def setUp(self):
        super(TestResolveOGUIDView, self).setUp()

        self.group = create(Builder('ogds_group')
                            .having(groupid='group', users=[self.user]))
        self.user2 = create(Builder('ogds_user')
                            .in_group(self.group)
                            .having(userid='x.john.doe',
                                    lastname='Doe',
                                    firstname='John'))

        self.actor1 = Actor.user(self.user.userid)
        self.actor2 = Actor.user(self.user2.userid)

    @browsing
    def test_list_groupmembers_view(self, browser):
        browser.login().open(view='list_groupmembers',
                             data={'group': self.group.groupid})

        self.assertSequenceEqual(
            [self.actor2.get_link(), self.actor1.get_link()],
            [each.normalized_outerHTML for each in
             browser.css('.member_listing li a')]
        )
