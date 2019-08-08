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
from opengever.disposition.delivery import IFilesystemTransportSettings
from opengever.disposition.testing import EnabledTransport
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2paths
from plone import api
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from zope.component import getSiteManager
from zope.component import getUtility

OFFERED_STATE = 'dossier-state-offered'
RESOLVED_STATE = 'dossier-state-resolved'
INACTIVE_STATE = 'dossier-state-inactive'


class TestDisposition(IntegrationTestCase):

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
        expected = 'Disposition Client1 Jan 01, 2014'

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
        self.assertEquals(['The dossier {} is already offered in a different '
                           'disposition.'.format(self.offered_dossier_to_archive.Title())],
                          browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_only_expired_dossiers_can_be_added(self, browser):
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
                ['The retention period of the selected dossiers is not expired.'],
                browser.css('.fieldErrorBox .error').text)

        with freeze(datetime(2021, 1, 1)):
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


class TestDispositionEditForm(IntegrationTestCase):

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
        browser.click_on('disposition-transition-dispose')

        self.assertEquals(['Item state changed.'], info_messages())
        self.assertTrue(self.disposition.has_sip_package())

        # Download is possible
        self.assertIn(
            'Download disposition package', browser.css('ul.actions li').text)

    @browsing
    def test_sip_package_is_removed_on_close(self, browser):
        self.login(self.records_manager, browser)

        self.disposition.store_sip_package()
        self.set_workflow_state('disposition-state-appraised', self.disposition)
        browser.open(self.disposition, view='overview')

        browser.click_on('disposition-transition-dispose')
        self.assertTrue(self.disposition.has_sip_package())

        with self.login(self.archivist, browser=browser):
            browser.open(self.disposition, view='overview')
            browser.click_on('disposition-transition-archive')

        browser.open(self.disposition, view='overview')
        browser.click_on('disposition-transition-close')

        self.assertEquals(['Item state changed.'], info_messages())
        self.assertFalse(self.disposition.has_sip_package())


class TestDispositionDelivery(IntegrationTestCase):

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
        statuses = scheduler.get_statuses()

        self.assertFalse(scheduler.is_scheduled_for_delivery())
        self.assertEqual({}, statuses)

        browser.open(self.disposition, view='overview')
        browser.click_on('disposition-transition-dispose')

        self.assertTrue(scheduler.is_scheduled_for_delivery())
        self.assertEqual({}, statuses)

        self.assertEquals(['Item state changed.'], info_messages())
        self.assertTrue(self.disposition.has_sip_package())

    @browsing
    def test_delivery_status_is_displayed(self, browser):
        self.login(self.records_manager, browser)

        self.set_workflow_state('disposition-state-appraised', self.disposition)

        self.enable_filesystem_transport()

        browser.open(self.disposition, view='overview')
        browser.click_on('disposition-transition-dispose')

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
        browser.click_on('disposition-transition-dispose')

        tbl_delivery_status = browser.css('#delivery-status').first
        self.assertEqual(
            [['enabled-transport', 'Scheduled for delivery'],
             ['filesystem', 'Scheduled for delivery']],
            tbl_delivery_status.lists())
