from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


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
                                .in_state('dossier-state-inactive'))
        self.dossier_c = create(Builder('dossier')
                                .within(self.repository)
                                .titled(u'Dossier C')
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
