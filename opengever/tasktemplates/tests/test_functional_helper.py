from mocker import ANY
from opengever.tasktemplates.browser.helper import interactive_user_helper
from plone.mocktestcase import MockTestCase


class TestFunctionalHelper(MockTestCase):
    """ Functional tests
    """

    def test_interactive_user_helper_interactive(self):
        """ Test interactive_user_helper-method
        """
        # Context
        mock_context = self.mocker.mock()

        self.replay()
        user = interactive_user_helper(mock_context, 'current_user')

        self.assertEqual('Current user', user)

    def test_interactive_user_helper_ogds(self):
        """ Test interactive_user_helper-method
        """
        # Context
        mock_context = self.mocker.mock()

        # Patch
        patch_ogds_author = self.mocker.replace(
            'opengever.tabbedview.helper.readable_ogds_author')
        self.expect(patch_ogds_author(ANY, ANY)).result('OGDS User')

        self.replay()

        user = interactive_user_helper(mock_context, '')

        self.assertEqual('OGDS User', user)
