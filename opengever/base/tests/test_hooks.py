from opengever.base.hooks import DEFAULT_EXTEDIT_ACTION_IDENTIFIER
from opengever.testing import FunctionalTestCase
from plone import api


class TestHooks(FunctionalTestCase):

    def test_default_external_edit_action_removed(self):
        actions_tool = api.portal.get_tool('portal_actions')
        category = actions_tool.get('document_actions')
        self.assertNotIn(DEFAULT_EXTEDIT_ACTION_IDENTIFIER, category,
                         'default "{}" action should have been removed by '
                         'post-installation hook'.format(
                             DEFAULT_EXTEDIT_ACTION_IDENTIFIER))
