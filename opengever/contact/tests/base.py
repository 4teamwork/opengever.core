from Products.PloneTestCase import ptc
from opengever.contact.testing import contact_integration_layer


class ContactTestCase(ptc.PloneTestCase):
    """Base class for integration tests."""

    layer = contact_integration_layer

