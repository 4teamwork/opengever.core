from opengever.base.sentry import maybe_report_exception
from opengever.disposition import _
from opengever.disposition.interfaces import ISIPTransport
from persistent.mapping import PersistentMapping
from ZODB.POSException import ConflictError
from zope.annotation import IAnnotations
from zope.component import getAdapters
from zope.globalrequest import getRequest
import logging
import sys
import traceback


TRANSPORT_STATUSES_KEY = 'opengever.disposition.delivery.transport_statuses'

STATUS_SCHEDULED = 'status_scheduled'
STATUS_SUCCESS = 'status_success'
STATUS_FAILED = 'status_failed'

DELIVERY_STATUS_LABELS = {
    STATUS_SCHEDULED: _(u'label_delivery_status_scheduled', default=u'Scheduled for delivery'),
    STATUS_SUCCESS: _(u'label_delivery_status_success', default=u'Delivered successfully'),
    STATUS_FAILED: _(u'label_delivery_status_failed', default=u'Delivery failed'),
}


class DeliveryScheduler(object):
    """The DeliveryScheduler takes care of scheduling SIP packages for delivery,
    performing scheduled deliveries by delegating to the respective transports,
    and tracking delivery statuses (per transport).
    """

    def __init__(self, disposition, parent_logger=None):
        self.disposition = disposition

        # When run via nightly job, the NightlyJobRunner's logger will be
        # passed in, so that the DeliveryScheduler's and the transporter's
        # log messages also can be logged to the nightly job logfile.
        if not parent_logger:
            parent_logger = logging.root

        self.parent_logger = parent_logger
        self.logger = logging.getLogger('opengever.disposition.delivery')
        self.logger.setLevel(logging.INFO)
        self.logger.parent = self.parent_logger

    def schedule_delivery(self, force=False):
        """Schedule the disposition's SIP for delivery with enabled transports.

        If `force` is `True`, the SIP will be rescheduled for delivery with
        all enabled transports, regardless of whether there already were any
        (successful or failed) delivery attempts.

        Otherwise, the SIP will be scheduled for delivery only for (enabled)
        transports that have not made a delivery attempt yet.
        """
        for name, transport in self.get_transports():
            # Only schedule for enabled transports
            if not transport.is_enabled():
                self.logger.info("Skip: Transport '%s' is disabled" % name)
                continue

            self.schedule_delivery_with(name, force=force)

    def schedule_delivery_with(self, name, force=False):
        """Schedule SIP for delivery with a particular transport.
        """
        statuses = self.get_statuses(create_if_missing=True)
        current_status = statuses.get(name)

        # Only schedule if no delivery was attempted yet
        # (Except when forcefully rescheduling)
        if force or current_status is None:
            self.mark_delivery_scheduled(name)

    def is_scheduled_for_delivery(self):
        """Whether the disposition is scheduled for delivery with any transport.
        """
        statuses = self.get_statuses()
        return any(s == STATUS_SCHEDULED for s in statuses.values())

    def is_scheduled_for_delivery_with(self, name):
        """Determine wheter this disposition is scheduled for delivery with
        transport `name`.
        """
        transport_status = self.get_statuses().get(name)
        return transport_status == STATUS_SCHEDULED

    def deliver(self):
        """Perform delivery of this disposition's SIP by delegating to transports.
        """
        for name, transport in self.get_transports():
            if not transport.is_enabled():
                self.logger.info("Skip: Transport '%s' is disabled" % name)
                continue

            if not self.is_scheduled_for_delivery_with(name):
                self.logger.info("Skip: Not scheduled for delivery with transport '%s'" % name)
                continue

            self.logger.info("Delivering using transport '%s'" % name)
            try:
                transport.deliver()
                self.mark_delivery_success(name)
                self.logger.info("Successful delivery using transport '%s'" % name)

            except ConflictError:
                raise

            except Exception as exc:
                self.logger.warn("Delivery with transport '%s' failed: %r" % (name, exc))
                self.mark_delivery_failure(name)
                e_type, e_value, tb = sys.exc_info()
                self.logger.error('Traceback:\n' + ''.join(traceback.format_tb(tb)))
                maybe_report_exception(self.disposition, getRequest(), e_type, e_value, tb)

    def get_statuses(self, create_if_missing=False):
        """Get the mapping of delivery statuses by transport.
        """
        ann = IAnnotations(self.disposition)
        if TRANSPORT_STATUSES_KEY not in ann and create_if_missing:
            ann[TRANSPORT_STATUSES_KEY] = PersistentMapping()
        return ann.get(TRANSPORT_STATUSES_KEY, {})

    def get_transports(self):
        """Return a list of (name, transport) tuples of all transports.
        """
        transports = getAdapters(
            [self.disposition, getRequest(), self.parent_logger],
            ISIPTransport
        )
        return sorted(transports)

    def mark_delivery_scheduled(self, name):
        self.logger.info("Scheduling delivery for transport: '%s'" % name)
        statuses = self.get_statuses(create_if_missing=True)
        statuses[name] = STATUS_SCHEDULED

    def mark_delivery_success(self, name):
        """Mark the delivery as successful with the transport `name`.
        """
        statuses = self.get_statuses(create_if_missing=True)
        statuses[name] = STATUS_SUCCESS

    def mark_delivery_failure(self, name):
        """Mark the delivery as failed with the transport `name`.
        """
        statuses = self.get_statuses(create_if_missing=True)
        statuses[name] = STATUS_FAILED
