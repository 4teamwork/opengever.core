from opengever.testing import IntegrationTestCase

BUMBLEBEE_NOTIFICATION_URL = 'http://bumblebee/YnVtYmxlYmVl/api/notifications'


class TestGeverJSVariables(IntegrationTestCase):
    """Test the base behavior with the help of businesscase dossier.
    """

    def test_geverjs_variables(self):
        self.login(self.regular_user)

        view = self.portal.restrictedTraverse('plone_javascript_variables.js')
        url_definition = "var bumblebee_notification_url = '{}';".format(
            BUMBLEBEE_NOTIFICATION_URL
        )
        self.assertIn(url_definition, view().split('\n'))
