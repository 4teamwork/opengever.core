from opengever.disposition.delivery import BaseTransport
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IFilesystemTransportSettings
from opengever.disposition.interfaces import ISIPTransport
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import CapturingLogHandler
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging
import shutil
import tempfile


@implementer(ISIPTransport)
@adapter(IDisposition, IBrowserRequest, logging.Logger)
class DummyTransport(BaseTransport):

    def deliver(self):
        pass

    def is_enabled(self):
        return False


class EnabledTransport(DummyTransport):

    def is_enabled(self):
        return True


class DisabledTransport(DummyTransport):

    def is_enabled(self):
        return False


class FailingTransport(EnabledTransport):

    def deliver(self):
        raise Exception('Boom')


class LogCapturingTestCase(IntegrationTestCase):
    """TestCase base class that allows to capture logged log records.
    """

    def setUp(self):
        super(LogCapturingTestCase, self).setUp()
        self.captured_log = CapturingLogHandler()
        logging.root.addHandler(self.captured_log)

    def tearDown(self):
        super(LogCapturingTestCase, self).tearDown()
        logging.root.removeHandler(self.captured_log)


class TestFilesystemTransportBase(LogCapturingTestCase):
    """TestCase base class to base FilesystemTransport tests on.

    This class
    - provides temporary directory that is isolated between tests
    - sets up log capturing
    - enables the FilesystemTransport (disabled by default)
    - makes sure a SIP is scheduled for delivery with the FS transport, like
      it would be if the FS transport was enabled all along
    """

    def setUp(self):
        super(TestFilesystemTransportBase, self).setUp()
        # Keep track of temporary files we create
        self.tempdir = tempfile.mkdtemp()

        # Enable FilesystemTransport
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFilesystemTransportSettings)
        settings.enabled = True
        settings.destination_directory = self.tempdir.decode('utf-8')

        # Scheduling deliveries would normally happen automatically after the
        # 'disposition-transition-dispose' transition.
        # However, because the disposition was created as part of the fixture,
        # and the FilesystemTransport was disabled at that time, the SIP
        # won't be scheduled for delivery yet.
        with self.login(self.records_manager):
            scheduler = DeliveryScheduler(self.disposition_with_sip)
            scheduler.schedule_delivery()

        self.captured_log.clear()

    def tearDown(self):
        super(TestFilesystemTransportBase, self).tearDown()
        # Clean up all temporary files we created
        shutil.rmtree(self.tempdir)
        self.captured_log.clear()
