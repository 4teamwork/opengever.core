from Products.CMFCore.utils import getToolByName
from opengever.testing import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from opengever.repository.interfaces import IRepositoryFolderRecords
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class TestLivesearchReply(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestLivesearchReply, self).setUp()
        self.grant('Contributor')

        # enable alternative title
        self.fti = getToolByName(self.portal, 'portal_types').get('opengever.repository.repositoryfolder')
        self.originalBehaviors = self.fti.behaviors
        self.fti.behaviors = self.fti.behaviors + ('opengever.repository.behaviors.alternativetitle.IAlternativeTitleBehavior', )

        # set alternative language to fr
        registry = getUtility(IRegistry)
        reg_proxy = registry.forInterface(IRepositoryFolderRecords)
        reg_proxy.alternative_language_code = u'fr'

        # create item with primary and alternative title
        create(Builder(u'repository')
                .within(self.portal)
                .titled(u'Weiterbildung')
                .having(alternative_title='Formation continue'))

    def test_livesearch_finds_nothing_if_non_existent_searchterm_is_given_and_responds_in_english_by_default(self):
        script = self.portal.restrictedTraverse("livesearch_reply")
        html = script("nonExistent")

        self.assertIn("No matching results found.", html)

    def test_livesearch_finds_german_result_and_responds_in_german_when_set(self):
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'de'

        script = self.portal.restrictedTraverse("livesearch_reply")
        html = script("weiterbildung")

        self.assertIn("Sofortsuche", html)
        self.assertIn("1. Weiterbildung", html)

    def test_livesearch_finds_french_result_and_responds_in_french_when_set(self):
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'

        script = self.portal.restrictedTraverse("livesearch_reply")
        html = script("formation")

        self.assertIn("Recherche instant", html)
        self.assertIn("1. Formation continue", html)
