from datetime import date
from dateutil.relativedelta import relativedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import transaction


class TestDossierListing(FunctionalTestCase):

    def setUp(self):
        super(TestDossierListing, self).setUp()

        self.repository = create(Builder('repository'))
        self.dossier_a = create(Builder('dossier')
                                .having(responsible=TEST_USER_ID,
                                        start=date(2015, 02, 10),
                                        end=date(2015, 02, 22))
                                .within(self.repository)
                                .titled(u'Dossier A'))
        self.dossier_b = create(Builder('dossier')
                                .within(self.repository)
                                .titled(u'Dossier B')
                                .having(start=date(2000, 1, 1),
                                        end=date(2005, 11, 6),
                                        retention_period=5)
                                .in_state('dossier-state-inactive'))
        self.dossier_c = create(Builder('dossier')
                                .within(self.repository)
                                .titled(u'Dossier C')
                                .having(start=date(2000, 1, 1),
                                        end=date(2000, 11, 6),
                                        retention_period=5)
                                .in_state('dossier-state-resolved'))

    @browsing
    def test_lists_only_active_dossiers_by_default(self, browser):
        browser.login().open(self.repository, view='tabbedview_view-dossiers')

        table = browser.css('.listing').first

        self.assertEquals([['',
                            'Reference Number',
                            'Title',
                            'Review state',
                            'Responsible',
                            'Start',
                            'End'],
                           ['',
                            'Client1 1 / 1',
                            'Dossier A',
                            'dossier-state-active',
                            'Test User (test_user_1_)',
                            '10.02.2015',
                            '22.02.2015']], table.lists())

    @browsing
    def test_list_every_dossiers_with_the_all_filter(self, browser):
        browser.login().open(self.repository,
                             view='tabbedview_view-dossiers',
                             data={'dossier_state_filter': 'filter_all'})

        table = browser.css('.listing').first
        self.assertEquals(['Dossier A', 'Dossier B', 'Dossier C'],
                          [row.get('Title') for row in table.dicts()])


    @browsing
    def test_active_closed_and_expired_filter_available(self, browser):
        browser.login().open(self.repository,
                             view='tabbedview_view-dossiers',
                             data={'dossier_state_filter': 'filter_all'})

        self.assertEquals(['all', 'Active', 'expired'],
                          browser.css('.state_filters a').text)

    @browsing
    def test_expired_filters_shows_only_dossiers_with_expired_retention_period(self, browser):
        browser.login()
        browser.open(
            self.repository,
            view='tabbedview_view-dossiers',
            data={'dossier_state_filter': 'filter_retention_expired'})

        table = browser.css('.listing').first
        self.assertEquals(['Dossier B', 'Dossier C'],
                          [row.get('Title') for row in table.dicts()])

        # update retention_period for dossier_b, so that its no longer expired
        IDossier(self.dossier_b).end = date.today() - relativedelta(years=1)
        self.dossier_b.reindexObject()
        transaction.commit()

        browser.open(
            self.repository,
            view='tabbedview_view-dossiers',
            data={'dossier_state_filter': 'filter_retention_expired'})

        table = browser.css('.listing').first
        self.assertEquals(['Dossier C'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_expired_filters_exclude_archived_dossiers(self, browser):
        create(Builder('dossier')
               .within(self.repository)
               .titled(u'Dossier D')
               .as_expired()
               .in_state('dossier-state-archived'))

        browser.login().open(
            self.repository,
            view='tabbedview_view-dossiers',
            data={'dossier_state_filter': 'filter_retention_expired'})

        table = browser.css('.listing').first
        self.assertEquals(['Dossier B', 'Dossier C'],
                          [row.get('Title') for row in table.dicts()])
