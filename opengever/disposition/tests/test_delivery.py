from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.delivery import STATUS_FAILED
from opengever.disposition.delivery import STATUS_SCHEDULED
from opengever.disposition.delivery import STATUS_SUCCESS
from opengever.disposition.interfaces import ISIPTransport
from opengever.disposition.testing import DisabledTransport
from opengever.disposition.testing import DummyTransport
from opengever.disposition.testing import EnabledTransport
from opengever.disposition.testing import FailingTransport
from opengever.disposition.testing import LogCapturingTestCase
from opengever.disposition.testing import TestFilesystemTransportBase
from opengever.testing import IntegrationTestCase
from os.path import join as pjoin
from zope.interface.verify import verifyObject
import os


class TestDeliveryScheduler(LogCapturingTestCase):

    def setUp(self):
        super(TestDeliveryScheduler, self).setUp()
        with self.login(self.records_manager):
            self.register_transport(EnabledTransport, 't-enabled')
            self.register_transport(DisabledTransport, 't-disabled')

            scheduler = DeliveryScheduler(self.disposition_with_sip)
            scheduler.schedule_delivery()
            self.captured_log.clear()

    def register_transport(self, cls, name):
        self.layer['load_zcml_string']("""
            <configure xmlns="http://namespaces.zope.org/zope">
                <adapter
                     name="%s"
                     factory="%s.%s"
                     />
            </configure>
        """ % (name, self.__module__, cls.__name__))

    def test_schedules_for_transports_with_no_delivery_attempt_yet(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        statuses = scheduler.get_statuses(create_if_missing=True)
        statuses.clear()

        scheduler.schedule_delivery()
        self.assertEqual({u't-enabled': STATUS_SCHEDULED}, statuses)

    def test_does_not_automatically_reschedule_successful_delivery(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        statuses = scheduler.get_statuses(create_if_missing=True)
        statuses.clear()

        statuses[u't-enabled'] = STATUS_SUCCESS
        scheduler.schedule_delivery()
        self.assertEqual({u't-enabled': STATUS_SUCCESS}, statuses)

    def test_does_not_automatically_reschedule_failed_delivery(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        statuses = scheduler.get_statuses(create_if_missing=True)
        statuses.clear()

        statuses[u't-enabled'] = STATUS_FAILED
        scheduler.schedule_delivery()
        self.assertEqual({u't-enabled': STATUS_FAILED}, statuses)

    def test_force_schedule_reschedules_all_states(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        statuses = scheduler.get_statuses(create_if_missing=True)
        statuses.clear()

        scheduler.schedule_delivery(force=True)
        self.assertEqual({u't-enabled': STATUS_SCHEDULED}, statuses)

        statuses[u't-enabled'] = STATUS_FAILED
        scheduler.schedule_delivery(force=True)
        self.assertEqual({u't-enabled': STATUS_SCHEDULED}, statuses)

        statuses[u't-enabled'] = STATUS_SUCCESS
        scheduler.schedule_delivery(force=True)
        self.assertEqual({u't-enabled': STATUS_SCHEDULED}, statuses)

        statuses[u't-enabled'] = STATUS_SCHEDULED
        scheduler.schedule_delivery(force=True)
        self.assertEqual({u't-enabled': STATUS_SCHEDULED}, statuses)

    def test_delivers_only_using_enabled_transports(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        scheduler.deliver()

        statuses = scheduler.get_statuses()
        statuses[u't-disabled'] = STATUS_SCHEDULED

        self.assertEqual([
            u"Skip: Transport 'filesystem' is disabled",
            u"Skip: Transport 't-disabled' is disabled",
            u"Delivering using transport 't-enabled'",
            u"Successful delivery using transport 't-enabled'"],
            self.captured_log.pop_msgs())

    def test_catches_transport_exceptions_and_sets_failed_status(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        statuses = scheduler.get_statuses(create_if_missing=True)
        statuses.clear()

        self.register_transport(FailingTransport, 't-failing')
        statuses[u't-failing'] = STATUS_SCHEDULED

        scheduler.deliver()

        self.assertIn(
            u"Delivering using transport 't-failing'",
            self.captured_log.msgs)

        self.assertIn(
            u"Delivery with transport 't-failing' failed: Exception('Boom',)",
            self.captured_log.msgs)

        self.assertEqual(STATUS_FAILED, statuses[u't-failing'])


class TestFilesystemTransport(TestFilesystemTransportBase):

    def setUp(self):
        super(TestFilesystemTransport, self).setUp()
        with self.login(self.records_manager):
            self.sip_filename = self.disposition_with_sip.get_sip_filename()
            self.dst_path = pjoin(self.tempdir, self.sip_filename)

    def test_sip_package_is_delivered_via_filesystem_transport(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        scheduler.deliver()

        self.assertEqual([
            u"Delivering using transport 'filesystem'",
            u"Transported %r to %r" % (self.sip_filename, self.dst_path),
            u"Successful delivery using transport 'filesystem'"],
            self.captured_log.pop_msgs())

        self.assertEqual([self.sip_filename], os.listdir(self.tempdir))

        with open(self.dst_path) as delivered_file:
            delivered_data = delivered_file.read()

        self.assertEqual(
            self.disposition_with_sip.get_sip_package().data,
            delivered_data)

    def test_doesnt_deliver_twice_unless_rescheduled(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        scheduler.deliver()

        self.assertEqual([
            u"Delivering using transport 'filesystem'",
            u"Transported %r to %r" % (self.sip_filename, self.dst_path),
            u"Successful delivery using transport 'filesystem'"],
            self.captured_log.pop_msgs())

        self.assertTrue(os.path.isfile(self.dst_path))

        os.remove(self.dst_path)
        scheduler.deliver()

        self.assertEqual([
            u"Skip: Not scheduled for delivery with transport 'filesystem'"],
            self.captured_log.pop_msgs())

        self.assertFalse(os.path.isfile(self.dst_path))

    def test_logs_when_overwriting_existing_sip(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)

        filename = '%s.zip' % self.disposition_with_sip.get_sip_name()
        dst_path = pjoin(self.tempdir, filename)

        scheduler.deliver()
        self.assertEqual([
            u"Delivering using transport 'filesystem'",
            u"Transported %r to %r" % (self.sip_filename, self.dst_path),
            u"Successful delivery using transport 'filesystem'"],
            self.captured_log.pop_msgs())

        scheduler.schedule_delivery(force=True)
        self.assertEqual([
            u"Scheduling delivery for transport: 'filesystem'"],
            self.captured_log.pop_msgs())

        scheduler.deliver()

        self.assertEqual([
            u"Delivering using transport 'filesystem'",
            u'Overwriting existing file %s' % dst_path,
            u"Transported %r to %r" % (self.sip_filename, self.dst_path),
            u"Successful delivery using transport 'filesystem'"],
            self.captured_log.pop_msgs())


class TestTransports(IntegrationTestCase):

    def register_transport(self, factory, name):
        getSiteManager().registerAdapter(factory, name=name)

    def test_all_transports_implement_interface(self):
        self.login(self.records_manager)

        # Also check our testing transports
        self.register_transport(DummyTransport, 't-dummy')
        self.register_transport(EnabledTransport, 't-enabled')
        self.register_transport(DisabledTransport, 't-disabled')
        self.register_transport(FailingTransport, 't-failing')

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        transports = scheduler.get_transports()
        for name, transport in transports:
            verifyObject(ISIPTransport, transport)
