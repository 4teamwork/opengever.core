from opengever.tasktemplates.browser.tasktemplates import preselected_helper
from plone.mocktestcase import MockTestCase


class TestFunctionalTemplates(MockTestCase):
    """ Functional tests
    """

    def test_preselected_helper(self):

        # Context
        mock_context = self.mocker.mock()
        get_site = self.mocker.replace('zope.app.component.hooks.getSite')
        self.expect(get_site()).result(mock_context)
        self.expect(mock_context.REQUEST).result(mock_context)

        self.replay()

        self.assertEquals(
            u'Yes', preselected_helper(mock_context, True))
        self.assertEquals('', preselected_helper(mock_context, False))
