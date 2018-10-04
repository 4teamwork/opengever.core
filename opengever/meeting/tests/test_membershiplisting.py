from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase


class TestMembershipListing(IntegrationTestCase):
    features = ('meeting',)

    maxDiff = None

    @browsing
    def test_filters(self, browser):
        self.login(self.meeting_user, browser)

        with freeze(datetime(2011, 6, 1)):
            browser.open(self.committee,
                         view='tabbedview_view-memberships',
                         data={'membership_state_filter': 'filter_membership_all'})
            self.assertItemsEqual(
                ['Neruda Pablo', u'Sch\xf6ller Heidrun', 'Wendler Jens', u'W\xf6lfl Gerda'],
                browser.css('#listing_container tbody tr td:first-child').text)

            browser.open(self.committee,
                         view='tabbedview_view-memberships',
                         data={'membership_state_filter': 'filter_membership_active'})
            self.assertItemsEqual(
                ['Neruda Pablo'],
                browser.css('#listing_container tbody tr td:first-child').text)

        with freeze(datetime(2015, 6, 1)):
            browser.open(self.committee,
                         view='tabbedview_view-memberships',
                         data={'membership_state_filter': 'filter_membership_active'})
            self.assertItemsEqual(
                [u'Sch\xf6ller Heidrun', 'Wendler Jens', u'W\xf6lfl Gerda'],
                browser.css('#listing_container tbody tr td:first-child').text)

    @browsing
    def test_entries_are_sorted_by_membership_id(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee,
                     view='tabbedview_view-memberships',
                     data={'membership_state_filter': 'filter_membership_all'})
        self.assertEqual(
            ['Neruda Pablo', u'Sch\xf6ller Heidrun', 'Wendler Jens', u'W\xf6lfl Gerda'],
            browser.css('#listing_container tbody tr td:first-child').text)

        member = create(
            Builder('member')
            .having(firstname="Hans", lastname="Schmidt")
            )

        create(
            Builder('membership')
            .having(
                committee=self.committee,
                member=member,
                date_from=datetime(2013, 1, 1),
                date_to=datetime(2018, 1, 1),
                )
            )

        browser.open(self.committee,
                     view='tabbedview_view-memberships',
                     data={'membership_state_filter': 'filter_membership_all'})
        self.assertEqual(
            ['Neruda Pablo', 'Schmidt Hans', u'Sch\xf6ller Heidrun', 'Wendler Jens', u'W\xf6lfl Gerda'],
            browser.css('#listing_container tbody tr td:first-child').text)
