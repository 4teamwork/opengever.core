from opengever.testing import IntegrationTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestRolesVocabulary(IntegrationTestCase):

    def test_roles_vocabulary_list_all_managed_roles(self):
        self.login(self.workspace_owner)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.RolesVocabulary')
        self.assertItemsEqual(
            ['Admin', 'Member', 'Guest'],
            [term.title for term in factory(context=self.portal)])
