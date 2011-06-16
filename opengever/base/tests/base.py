from Products.PloneTestCase import ptc
from opengever.base.tests.layer import base_integration_layer


class OpengeverBaseTestCase(ptc.PloneTestCase):
    """Base class for opengever.base tests."""

    layer = base_integration_layer