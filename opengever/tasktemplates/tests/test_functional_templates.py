from opengever.tasktemplates.browser.tasktemplates import preselected_helper
from plone.mocktestcase import MockTestCase


class TestFunctionalTemplates(MockTestCase):
    """ Functional tests
    """

    def test_preselected_helper(self):

        # Context
        mock_context = self.mocker.mock()

        self.replay()

        self.assertEquals(
            'preselected_yes', preselected_helper(mock_context, True))
        self.assertEquals('', preselected_helper(mock_context, False))
