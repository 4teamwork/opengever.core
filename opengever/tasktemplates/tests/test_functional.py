from opengever.tasktemplates.testing \
    import OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING
import unittest2 as unittest


class TestTaskTemplatesIntegration(unittest.TestCase):

    layer = OPENGEVER_TASKTEMPLATES_INTEGRATION_TESTING

    def test_functional(self):
        """ Functional tests
        """

        pass