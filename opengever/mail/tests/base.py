from opengever.mail.testing import OPENGEVER_MAIL_INTEGRATION_TESTING
import unittest2 as unittest

class MailTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = OPENGEVER_MAIL_INTEGRATION_TESTING
