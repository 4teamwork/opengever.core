from opengever.testing import IntegrationTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestDocumentTemplatesVocabulary(IntegrationTestCase):

    def test_roles_vocabulary_list_all_managed_roles(self):
        self.login(self.regular_user)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.dossier.DocumentTemplatesVocabulary')

        self.assertItemsEqual(
            [u'T\xc3\xb6mpl\xc3\xb6te Mit',
             u'T\xc3\xb6mpl\xc3\xb6te Normal',
             u'T\xc3\xb6mpl\xc3\xb6te Ohne',
             u'T\xc3\xb6mpl\xc3\xb6te Sub'],
            [term.title for term in factory(context=self.portal)])
