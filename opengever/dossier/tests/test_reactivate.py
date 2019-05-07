from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone.protect import createToken


class TestReactivating(IntegrationTestCase):

    def setUp(self):
        super(TestReactivating, self).setUp()
        with self.login(self.regular_user):
            self.set_workflow_state('dossier-state-resolved',
                                    self.resolvable_dossier,
                                    self.resolvable_subdossier)

    def reactivate(self, dossier, browser):
        return browser.open(dossier,
                            view='transition-reactivate',
                            data={'_authenticator': createToken()})

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(error_msgs, error_messages())

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEquals(dossier.absolute_url(), browser.url)
        statusmessages.assert_no_error_messages()
        self.assertEquals(info_msgs, info_messages())

    @browsing
    def test_reactivating_a_resolved_dossier_succesfully(self, browser):
        self.login(self.secretariat_user, browser)

        self.reactivate(self.resolvable_dossier, browser)

        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)
        self.assert_success(self.resolvable_dossier, browser,
                            ['Dossiers successfully reactivated.'])

    @browsing
    def test_reactivating_a_main_dossier_reactivates_subdossiers_recursively(self, browser):
        self.login(self.secretariat_user, browser)
        subsub = create(Builder('dossier')
                        .within(self.resolvable_subdossier)
                        .in_state('dossier-state-resolved'))

        self.reactivate(self.resolvable_dossier, browser)

        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)
        self.assert_workflow_state('dossier-state-active', self.resolvable_subdossier)
        self.assert_workflow_state('dossier-state-active', subsub)

    @browsing
    def test_reactivating_a_subdossier_of_a_resolved_dossier_is_not_possible(self, browser):
        self.login(self.secretariat_user, browser)

        self.reactivate(self.resolvable_subdossier, browser)

        self.assert_errors(self.resolvable_subdossier, browser,
                           ["It isn't possible to reactivate a sub dossier."])
        self.assert_workflow_state('dossier-state-resolved',
                                   self.resolvable_subdossier)

    @browsing
    def test_resets_end_dates_recursively(self, browser):
        end_date = date(2013, 2, 21)
        end_date_index = self.dateindex_value_from_datetime(end_date)

        self.login(self.secretariat_user, browser)
        IDossier(self.resolvable_dossier).end = end_date
        IDossier(self.resolvable_subdossier).end = end_date
        self.resolvable_dossier.reindexObject(idxs=['end'])
        self.resolvable_subdossier.reindexObject(idxs=['end'])
        subsub = create(Builder('dossier')
                        .within(self.resolvable_subdossier)
                        .having(end=end_date)
                        .in_state('dossier-state-resolved'))

        self.assert_index_value(end_date_index, 'end', self.resolvable_dossier,
                                self.resolvable_subdossier, subsub)
        self.assert_metadata_value(end_date, 'end', self.resolvable_dossier,
                                   self.resolvable_subdossier, subsub)

        self.reactivate(self.resolvable_dossier, browser)

        self.assert_index_value('', 'end', self.resolvable_dossier,
                                self.resolvable_subdossier, subsub)
        self.assert_metadata_value(None, 'end', self.resolvable_dossier,
                                   self.resolvable_subdossier, subsub)
        self.assertIsNone(IDossier(self.resolvable_dossier).end)
        self.assertIsNone(IDossier(self.resolvable_subdossier).end)
        self.assertIsNone(IDossier(subsub).end)
