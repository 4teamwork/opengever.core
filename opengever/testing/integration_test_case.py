from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from unittest2 import TestCase


class IntegrationTestCase(TestCase):
    layer = OPENGEVER_INTEGRATION_TESTING

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = portal = self.layer['portal']
        self.request = self.layer['request']

        self.repository_root = portal['repository-root']
