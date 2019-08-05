from opengever.base.sentry import maybe_report_exception
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IFilesystemTransportSettings
from opengever.disposition.interfaces import ISIPTransport
from os.path import abspath
from os.path import expanduser
from os.path import join as pjoin
from persistent.mapping import PersistentMapping
from plone.registry.interfaces import IRegistry
from ZODB.POSException import ConflictError
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging
import os
import shutil
import stat
import sys


TRANSPORT_STATUSES_KEY = 'opengever.disposition.delivery.transport_statuses'

STATUS_SCHEDULED = 'status_scheduled'
STATUS_SUCCESS = 'status_success'
STATUS_FAILED = 'status_failed'


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
        statuses = self.get_statuses(create_if_missing=True)
        for name, transport in self.get_transports():
            # Only schedule for enabled transports
            if not transport.is_enabled():
                self.logger.info("Skip: Transport '%s' is disabled" % name)
                continue

            current_status = statuses.get(name)

            # Only schedule if no delivery was attempted yet
            # (Except when forcefully rescheduling)
            if force or current_status is None:
                self.logger.info("Scheduling delivery for transport: '%s'" % name)
                statuses[name] = STATUS_SCHEDULED

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
                self.logger.info("Delivery with transport '%s' failed: %r" % (name, exc))
                self.mark_delivery_failure(name)
                e_type, e_value, tb = sys.exc_info()
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


class BaseTransport(object):
    """Base class for Transports that sets up proper logging.
    """

    def __init__(self, disposition, request, parent_logger):
        self.disposition = disposition
        self.request = request
        self.parent_logger = parent_logger

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)
        self.log.parent = parent_logger


@implementer(ISIPTransport)
@adapter(IDisposition, IBrowserRequest, logging.Logger)
class FilesystemTransport(BaseTransport):
    """Transport that copies the SIP to a filesystem location specified by
    the IFilesystemTransportSettings.destination_directory registry entry.
    """

    def deliver(self):
        """Delivers the SIP by copying it to the destination_directory.
        """
        destination_dir = self._get_destination_directory()
        assert os.path.isdir(destination_dir)
        sip = self.disposition.get_sip_package()

        blob_path = sip._blob.committed()
        filename = self.disposition.get_sip_filename()
        destination_path = pjoin(destination_dir, filename)

        if os.path.isfile(destination_path):
            self.log.warn("Overwriting existing file %s" % destination_path)

        shutil.copy2(blob_path, destination_path)

        # Make delivered file writable for owner
        st = os.stat(destination_path)
        os.chmod(destination_path, st.st_mode | stat.S_IWUSR)

        self.log.info("Transported %r to %r" % (filename, destination_path))

    def is_enabled(self):
        settings = self._get_settings()
        return settings.enabled

    def _get_destination_directory(self):
        settings = self._get_settings()
        destination_dir = settings.destination_directory
        destination_dir = abspath(expanduser(destination_dir.strip()))
        return destination_dir

    def _get_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFilesystemTransportSettings)
        return settings
