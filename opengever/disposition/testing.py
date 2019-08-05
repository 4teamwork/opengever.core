from opengever.disposition.delivery import BaseTransport
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import ISIPTransport
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import CapturingLogHandler
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging


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
