from Products.PloneTestCase import ptc
from opengever.mail.testing import mail_integration_layer


class MailTestCase(ptc.PloneTestCase):
    """Base class for integration tests."""

    layer = mail_integration_layer
