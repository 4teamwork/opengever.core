from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestUserListing(FunctionalTestCase):

    def setUp(self):
        super(TestUserListing, self).setUp()

        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

        create(Builder('ogds_user')
               .having(userid=u'peter.mueller',
                       firstname=u'Peter',
                       lastname=u'M\xfcller'))
        create(Builder('ogds_user')
               .having(userid=u'hugo.boss',
                       firstname=u'Hugo',
                       lastname=u'B\xf6ss'))
        create(Builder('ogds_user')
               .having(userid=u'sandra.mustermann',
                       firstname=u'Sandra',
                       lastname=u'Mustermann',
                       active=False))

    def _get_user_data_listing(self, browser):
        """Return the user listing displayed in the browser without header."""
        return browser.css('.listing').first.lists()[1:]

    @browsing
    def test_display_only_active_users_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-users')

        self.assertEquals([
                [u'B\xf6ss', 'Hugo', 'hugo.boss', 'test@example.org',
                 '', '', '', 'Yes'],
                [u'M\xfcller', 'Peter', 'peter.mueller', 'test@example.org',
                 '', '', '', 'Yes'],
                ['Test', 'User', 'test_user_1_', 'test@example.org',
                 '', '', '', 'Yes'],
            ],
            self._get_user_data_listing(browser)
        )

    @browsing
    def test_display_all_users_when_all_filter_enabled(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-users',
            data={'user_state_filter': 'filter_all'})

        self.assertEquals([
                [u'B\xf6ss', 'Hugo', 'hugo.boss', 'test@example.org',
                 '', '', '', 'Yes'],
                [u'Mustermann', 'Sandra', 'sandra.mustermann',
                 'test@example.org', '', '', '', 'No'],
                [u'M\xfcller', 'Peter', 'peter.mueller', 'test@example.org',
                 '', '', '', 'Yes'],
                ['Test', 'User', 'test_user_1_', 'test@example.org',
                 '', '', '', 'Yes'],
            ],
            self._get_user_data_listing(browser)
        )
