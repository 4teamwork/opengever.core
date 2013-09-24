from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import FunctionalTestCase
from opengever.repository.interfaces import IRepositoryFolderRecords
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class TestAlternativeTitleAccessor(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestAlternativeTitleAccessor, self).setUp()
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()
        self.fti = getToolByName(self.portal, 'portal_types').get('opengever.repository.repositoryfolder')
        self.originalBehaviors = self.fti.behaviors
        self.fti.behaviors = self.fti.behaviors + ('opengever.repository.behaviors.alternativetitle.IAlternativeTitleBehavior', )

        # set alternative language to fr
        registry = getUtility(IRegistry)
        reg_proxy = registry.forInterface(IRepositoryFolderRecords)
        reg_proxy.alternative_language_code = u'fr'

    def tearDown(self):
        self.fti.behaviors = self.originalBehaviors

    def test_returns_german_title_when_preferred_lang_is_de(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'de'

        repository = create(Builder('repository')
                .titled('Weiterbildung')
                .having(alternative_title='Formation continue'))

        self.assertEquals(
            "1. " + repository.effective_title,
            repository.Title())

    def test_returns_alternative_title_when_preferred_title_is_fr(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'
        repository = create(Builder('repository')
                .titled('Weiterbildung')
                .having(alternative_title='Formation continue'))

        self.assertEquals(
            "1. Formation continue",
            repository.Title())

    def test_returns_title_field_when_preferred_lang_is_not_supported(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'it'
        repository = create(Builder('repository')
                .titled('Weiterbildung')
                .having(alternative_title='Formation continue'))

        self.assertEquals(
            "1. " + repository.effective_title,
            repository.Title())
