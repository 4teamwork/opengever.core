from opengever.testing import OPENGEVER_INTEGRATION_TESTING
import unittest2 as unittest

class MailTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = OPENGEVER_INTEGRATION_TESTING
