from ftw.bumblebee import get_service_v3
from opengever.bumblebee.service import GeverBumblebeeService
from opengever.testing import FunctionalTestCase


class TestIsBumblebeeFeatureEnabled(FunctionalTestCase):

    def test_bumblebee_service_registration(self):
        service = get_service_v3()
        self.assertIsInstance(service, GeverBumblebeeService)
