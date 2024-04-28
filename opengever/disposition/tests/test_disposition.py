from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.delivery import STATUS_SCHEDULED
from opengever.disposition.interfaces import IFilesystemTransportSettings
from opengever.disposition.testing import EnabledTransport
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import obj2paths
from opengever.testing.integration_test_case import SolrIntegrationTestCase
from plone import api
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from zope.component import getSiteManager
from zope.component import getUtility


OFFERED_STATE = 'dossier-state-offered'
RESOLVED_STATE = 'dossier-state-resolved'
INACTIVE_STATE = 'dossier-state-inactive'


class TestDisposition(SolrIntegrationTestCase):

    def test_id_is_sequence_number_prefixed_with_disposition(self):
        self.login(self.records_manager)
        disposition = create(Builder('disposition'))
        self.assertEquals('disposition-1', self.disposition.getId())
        self.assertEquals('disposition-2', self.disposition_with_sip.getId())
        self.assertEquals('disposition-3', disposition.getId())

    @browsing
    def test_title_is_prefilled_with_default_suggestion(self, browser):
        """Expected format:
        Disposition {adminiunit-abbreviation} {today's date}'.
        """
        expected = 'Offer Client1 Jan 01, 2014'

        self.login(self.archivist, browser)
        with freeze(datetime(2014, 1, 1)):
            browser.open(self.leaf_repofolder,
                         view="++add++opengever.disposition.disposition")

            self.assertEquals(
                expected, browser.forms.get('form').find_field('Title').value)

    @browsing
    def test_can_be_added(self, browser):
        self.login(self.records_manager, browser)

        browser.open(self.repository_root)
        factoriesmenu.add('Disposition')
        with freeze(datetime(2037, 1, 1)):
            browser.fill({'Dossiers': [self.inactive_dossier,
                                       self.expired_dossier]})
            browser.find('Save').click()

        self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_selected_dossiers_in_the_list_are_preselected(self, browser):
        self.login(self.records_manager, browser)
        self.disposition.dossiers = []

        dossiers_to_add = [self.inactive_dossier, self.expired_dossier]
        data = {'paths:list': obj2paths(dossiers_to_add),
                '_authenticator': createToken()}

        with freeze(datetime(2037, 1, 1)):
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)

            browser.find('Save').click()

        self.assertEquals(dossiers_to_add,
                          [rel.to_object for rel in browser.context.dossiers])

    @browsing
    def test_selected_dossiers_in_active_states_are_skipped(self, browser):
        self.login(self.records_manager, browser)

        data = {'paths:list': obj2paths([self.empty_dossier]),
                '_authenticator': createToken()}

        browser.open(self.repository_root,
                     view='++add++opengever.disposition.disposition',
                     data=data)
        browser.find('Save').click()

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(['Required input is missing.'],
                          browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_already_offered_dossiers_cant_be_selected(self, browser):
        self.login(self.records_manager, browser)

        data = {'paths:list': obj2paths([self.offered_dossier_to_archive]),
                '_authenticator': createToken()}
        browser.open(self.repository_root,
                     view='++add++opengever.disposition.disposition',
                     data=data)
        browser.find('Save').click()

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(['The dossier {} is already in another offer.'
                           ''.format(self.offered_dossier_to_archive.Title())],
                          browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_only_expired_dossiers_can_be_added_by_default(self, browser):
        self.login(self.records_manager, browser)

        data = {'paths:list': obj2paths([self.expired_dossier]),
                '_authenticator': createToken()}

        self.assertEqual(date(2000, 12, 31), IDossier(self.expired_dossier).end)

        with freeze(datetime(2001, 1, 1)):
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)

            browser.find('Save').click()

            self.assertEquals(['There were some errors.'], error_messages())
            self.assertEquals(
                ['The retention period of the selected dossiers has not expired yet.'],
                browser.css('.fieldErrorBox .error').text)

        with freeze(datetime(2021, 1, 1)):
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)

            browser.find('Save').click()

            self.assertEquals([], error_messages())
            self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_non_expired_dossiers_can_be_added_with_disregard_retention_period(self, browser):
        self.login(self.records_manager, browser)
        self.activate_feature('disposition-disregard-retention-period')

        data = {'paths:list': obj2paths([self.expired_dossier]),
                '_authenticator': createToken()}

        with freeze(datetime(2001, 1, 1)):
            self.assertFalse(self.expired_dossier.is_retention_period_expired())
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)

            browser.find('Save').click()

            self.assertEquals([], error_messages())
            self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_attached_dossier_are_set_to_offered_state(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2037, 1, 1)):
            data = {'paths:list': obj2paths([self.expired_dossier, self.inactive_dossier]),
                    '_authenticator': createToken()}
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)
            browser.find('Save').click()

        self.assertEquals(OFFERED_STATE, api.content.get_state(self.expired_dossier))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.inactive_dossier))

    @browsing
    def test_date_of_submission_is_set_today_for_attached_dossiers(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2037, 1, 1)):
            data = {'paths:list': obj2paths([self.expired_dossier, self.inactive_dossier]),
                    '_authenticator': createToken()}
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)
            browser.find('Save').click()

            self.assertEquals(date.today(),
                              ILifeCycle(self.expired_dossier).date_of_submission)
            self.assertEquals(date.today(),
                              ILifeCycle(self.inactive_dossier).date_of_submission)

    def test_has_dossiers_with_pending_permissions_changes(self):
        self.login(self.records_manager)
        self.assertTrue(self.disposition.dossiers_with_missing_permissions)
        self.assertFalse(self.disposition.dossiers_with_extra_permissions)
        self.assertTrue(self.disposition.has_dossiers_with_pending_permissions_changes)

        self.disposition.dossiers_with_missing_permissions = []
        self.assertFalse(self.disposition.has_dossiers_with_pending_permissions_changes)

        self.disposition.dossiers_with_extra_permissions = [self.expired_dossier.UID()]
        self.assertTrue(self.disposition.has_dossiers_with_pending_permissions_changes)

    @browsing
    def test_dossiers_with_missing_permissions_are_stored(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2037, 1, 1)), self.observe_children(self.repository_root) as children:
            data = {'paths:list': obj2paths([self.expired_dossier, self.inactive_dossier]),
                    '_authenticator': createToken()}
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)
            browser.find('Save').click()

        self.assertEqual(len(children["added"]), 1)
        disposition = children["added"].pop()
        self.assertItemsEqual([self.expired_dossier.UID(),
                               self.inactive_dossier.UID()],
                              disposition.dossiers_with_missing_permissions)

    @browsing
    def test_dossiers_with_missing_or_extra_permissions_are_updated_correctly(self, browser):
        self.login(self.records_manager, browser)

        self.assertItemsEqual(
            [self.offered_dossier_to_archive.UID(),
             self.offered_dossier_to_destroy.UID()],
            self.disposition.dossiers_with_missing_permissions)

        self.assertEqual([], self.disposition.dossiers_with_extra_permissions)

        # We fake that permissions have been updated for offered_dossier_to_destroy
        self.disposition.dossiers_with_missing_permissions.remove(
            self.offered_dossier_to_destroy.UID())

        browser.open(self.disposition, view='edit')
        browser.fill({'Dossiers': [self.expired_dossier]})
        browser.find('Save').click()

        self.assertItemsEqual(
            [self.expired_dossier.UID()],
            self.disposition.dossiers_with_missing_permissions)

        # self.offered_dossier_to_archive does not have extra permissions
        # as the permissions had not been set
        self.assertItemsEqual(
            [self.offered_dossier_to_destroy.UID()],
            self.disposition.dossiers_with_extra_permissions)

    @browsing
    def test_dossier_stats_are_updated_on_creation(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2037, 1, 1)), self.observe_children(self.repository_root) as children:
            data = {'paths:list': obj2paths([self.expired_dossier, self.inactive_dossier]),
                    '_authenticator': createToken()}
            browser.open(self.repository_root,
                         view='++add++opengever.disposition.disposition',
                         data=data)
            browser.find('Save').click()

        self.assertEqual(len(children["added"]), 1)
        disposition = children["added"].pop()
        expected = {
            'createinactivedossier00000000001': {
                'docs_size': 19,
                'docs_count': 1,
            },
            'createexpireddossier000000000001': {
                'docs_size': 9,
                'docs_count': 1,
            }}
        self.assertEqual(expected, disposition.stats_by_dossier)


class TestDispositionEditForm(SolrIntegrationTestCase):

    def test_initial_states(self):
        self.login(self.regular_user)
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.offered_dossier_to_archive))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.offered_dossier_to_destroy))
        self.assertEquals(RESOLVED_STATE, api.content.get_state(self.expired_dossier))
        self.assertEquals(INACTIVE_STATE, api.content.get_state(self.inactive_dossier))

    @browsing
    def test_set_added_dossiers_to_offered_state(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2037, 1, 1)):
            browser.open(self.disposition, view='edit')
            browser.fill({'Dossiers': [self.offered_dossier_to_archive,
                                       self.offered_dossier_to_destroy,
                                       self.expired_dossier,
                                       self.inactive_dossier]})
            browser.find('Save').click()

        self.assertEquals(OFFERED_STATE, api.content.get_state(self.offered_dossier_to_archive))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.offered_dossier_to_destroy))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.expired_dossier))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.inactive_dossier))

    @browsing
    def test_set_dropped_dossiers_to_former_state(self, browser):
        self.login(self.records_manager, browser)

        browser.open(self.disposition, view='edit')
        browser.fill({'Dossiers': [self.expired_dossier]})
        browser.find('Save').click()

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.offered_dossier_to_archive))
        self.assertEquals('dossier-state-inactive',
                          api.content.get_state(self.offered_dossier_to_destroy))
        self.assertEquals(OFFERED_STATE, api.content.get_state(self.expired_dossier))

    @browsing
    def test_reset_date_of_submission_for_dropped_dossiers(self, browser):
        self.login(self.records_manager, browser)

        browser.open(self.disposition, view='edit')
        browser.fill({'Dossiers': [self.expired_dossier]})
        browser.find('Save').click()

        self.assertEquals(
            None, ILifeCycle(self.offered_dossier_to_archive).date_of_submission)
        self.assertEquals(
            None, ILifeCycle(self.offered_dossier_to_destroy).date_of_submission)
        self.assertEquals(
            date.today(), ILifeCycle(self.expired_dossier).date_of_submission)

    @browsing
    def test_sip_package_is_genarated_and_stored_on_dispose(self, browser):
        self.login(self.records_manager, browser)

        self.set_workflow_state('disposition-state-appraised', self.disposition)

        browser.open(self.disposition, view='overview')
        browser.click_on('Submit disposition')

        self.assertEquals(['Item state changed.'], info_messages())
        self.assertTrue(self.disposition.has_sip_package())

        # Download is possible
        self.assertIn(
            'Download disposal package', browser.css('ul.actions li').text)

    @browsing
    def test_sip_package_is_removed_on_close(self, browser):
        self.login(self.records_manager, browser)

        self.disposition.store_sip_package()
        self.set_workflow_state('disposition-state-appraised', self.disposition)
        browser.open(self.disposition, view='overview')

        browser.click_on('Submit disposition')
        self.assertTrue(self.disposition.has_sip_package())

        with self.login(self.archivist, browser=browser):
            browser.open(self.disposition, view='overview')
            browser.click_on('Confirm archival')

        browser.open(self.disposition, view='overview')
        browser.click_on('Dispose of dossiers')

        self.assertEquals(['Item state changed.'], info_messages())
        self.assertFalse(self.disposition.has_sip_package())

    @browsing
    def test_can_overwrite_transferring_office(self, browser):
        self.login(self.records_manager, browser)
        self.assertEqual(u'Hauptmandant', self.disposition.transferring_office)

        browser.open(self.disposition, view='edit')
        browser.fill({'Transferring office (AktenbildnerName)': "Foo"})
        browser.find('Save').click()
        self.assertEqual(u'Foo', self.disposition.transferring_office)


class TestDispositionDelivery(SolrIntegrationTestCase):

    def enable_filesystem_transport(self):
        # Enable FilesystemTransport
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFilesystemTransportSettings)
        settings.enabled = True
        settings.destination_directory = u'/tmp/will-not-be-used'

    @browsing
    def test_sip_package_is_scheduled_for_delivery_on_dispose(self, browser):
        self.login(self.records_manager, browser)

        self.set_workflow_state('disposition-state-appraised', self.disposition)

        self.enable_filesystem_transport()
        scheduler = DeliveryScheduler(self.disposition)

        self.assertFalse(scheduler.is_scheduled_for_delivery())
        self.assertEqual({}, scheduler.get_statuses())

        browser.open(self.disposition, view='overview')
        browser.click_on('Submit disposition')

        self.assertTrue(scheduler.is_scheduled_for_delivery())
        self.assertEqual({u'filesystem': STATUS_SCHEDULED},
                          scheduler.get_statuses())

        self.assertEquals(['Item state changed.'], info_messages())
        self.assertTrue(self.disposition.has_sip_package())

    @browsing
    def test_delivery_status_is_displayed(self, browser):
        self.login(self.records_manager, browser)

        self.set_workflow_state('disposition-state-appraised', self.disposition)

        self.enable_filesystem_transport()

        browser.open(self.disposition, view='overview')
        browser.click_on('Submit disposition')

        tbl_delivery_status = browser.css('#delivery-status').first
        self.assertEqual(
            [['Scheduled for delivery']],
            tbl_delivery_status.lists())

    @browsing
    def test_delivery_status_is_displayed_per_transport_for_multiple_transports(self, browser):
        self.login(self.records_manager, browser)

        self.set_workflow_state('disposition-state-appraised', self.disposition)

        getSiteManager().registerAdapter(EnabledTransport, name='enabled-transport')
        self.enable_filesystem_transport()

        browser.open(self.disposition, view='overview')
        browser.click_on('Submit disposition')

        tbl_delivery_status = browser.css('#delivery-status').first
        self.assertEqual(
            [['enabled-transport', 'Scheduled for delivery'],
             ['filesystem', 'Scheduled for delivery']],
            tbl_delivery_status.lists())
