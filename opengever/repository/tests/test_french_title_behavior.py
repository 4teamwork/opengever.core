from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.contentlisting.interfaces import IContentListingObject


class TestFrenchTitleBehavior(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestFrenchTitleBehavior, self).setUp()
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()

    def test_Title_returns_title_in_the_preferred_language(self):
        repository = create(Builder('repository')
               .having(title='Weiterbildung',
                       title_fr='Formation continue'))

        repository.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'

        self.assertEquals(
            '1. Formation continue',
            IContentListingObject(obj2brain(repository)).Title())

    def test_Title_returns_title_when_title_in_preffered_language_does_not_exist(self):
        repository = create(Builder('repository')
               .having(title=u'Weiterbildung', ))

        repository.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'it'

        self.assertEquals(
            '1. Weiterbildung',
            IContentListingObject(obj2brain(repository)).Title())
