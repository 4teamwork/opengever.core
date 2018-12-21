from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestListGroupMembers(IntegrationTestCase):

    @browsing
    def test_list_groupmembers_view(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='list_groupmembers', data={'group': 'projekt_b'})

        self.assertSequenceEqual(
            ['http://nohost/plone/@@user-details/herbert.jager',
             'http://nohost/plone/@@user-details/franzi.muller'],
            [link.get('href') for link in browser.css('.member_listing li a')])

    @browsing
    def test_list_groupmembers_view_with_empty_group(self, browser):
        self.login(self.regular_user, browser=browser)

        group = create(Builder('ogds_group')
                       .having(groupid='empty_group'))
        browser.open(view='list_groupmembers', data={'group': group.groupid})
        self.assertEqual('There are no members in this group.',
                         browser.css('p').text[0])
