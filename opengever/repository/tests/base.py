from Products.PloneTestCase import ptc
from opengever.repository.tests.layer import repository_integration_layer


class OpengeverRepositoryTestCase(ptc.PloneTestCase):
    """Base class for opengever.repository tests."""

    layer = repository_integration_layer