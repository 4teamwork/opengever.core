from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.delivery import STATUS_FAILED
from opengever.disposition.delivery import STATUS_SCHEDULED
from opengever.disposition.delivery import STATUS_SUCCESS
from opengever.disposition.testing import DisabledTransport
from opengever.disposition.testing import EnabledTransport
from opengever.disposition.testing import FailingTransport
from opengever.disposition.testing import LogCapturingTestCase


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
