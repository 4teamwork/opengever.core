from opengever.testing import IntegrationTestCase


class TestPendingSigningJobStorage(IntegrationTestCase):
    def test_can_store_and_load_data(self):
        self.login(self.regular_user)

    def test_data_is_stored_on_the_context(self):
        self.login(self.regular_user)
