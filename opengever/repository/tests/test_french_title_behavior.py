from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import FunctionalTestCase


class TestFrenchTitleAccessor(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestFrenchTitleAccessor, self).setUp()
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()
        self.fti = getToolByName(self.portal, 'portal_types').get('opengever.repository.repositoryfolder')
        self.originalBehaviors = self.fti.behaviors
        self.fti.behaviors = self.fti.behaviors + ('opengever.repository.behaviors.frenchtitle.IFrenchTitleBehavior', )

    def tearDown(self):
        self.fti.behaviors = self.originalBehaviors

    def test_returns_german_title_when_preferred_lang_is_de(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'de'

        repository = create(Builder('repository')
                .titled('Weiterbildung')
                .having(title_fr='Formation continue'))

        self.assertEquals(
            "1. " + repository.effective_title,
            repository.Title())

    def test_returns_french_title_when_preferred_title_is_fr(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'
        repository = create(Builder('repository')
                .titled('Weiterbildung')
                .having(title_fr='Formation continue'))

        self.assertEquals(
            "1. Formation continue",
            repository.Title())

    def test_returns_title_field_when_preferred_lang_is_not_supported(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'it'
        repository = create(Builder('repository')
                .titled('Weiterbildung')
                .having(title_fr='Formation continue'))

        self.assertEquals(
            "1. " + repository.effective_title,
            repository.Title())
