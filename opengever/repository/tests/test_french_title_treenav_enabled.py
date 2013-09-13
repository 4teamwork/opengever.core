from Products.CMFCore.utils import getToolByName
from opengever.testing import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING


class TestFrenchTitleTreenav(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestFrenchTitleTreenav, self).setUp()
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()
        # enable french title
        self.fti = getToolByName(self.portal, 'portal_types').get('opengever.repository.repositoryfolder')
        self.originalBehaviors = self.fti.behaviors
        self.fti.behaviors = self.fti.behaviors + ('opengever.repository.behaviors.frenchtitle.IFrenchTitleBehavior', )

    def tearDown(self):
        self.fti.behaviors = self.originalBehaviors

    def test_retuns_french_title_if_enabled_and_set(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'
        # define tree with german and french title
        reporoot = create(Builder('repository_root')
                .titled(u'Root'))
        repo = create(Builder(u'repository')
                .within(reporoot)
                .titled(u'Weiterbildung')
                .having(title_fr='Formation continue'))

        html = repo.restrictedTraverse('tree').render()

        self.assertIn("1. Formation continue", html)

    def test_retuns_default_title_when_french_enabled_but_not_set(self):
        # define tree withOUT french title
        reporoot = create(Builder('repository_root')
                .titled(u'Root'))
        repo = create(Builder(u'repository')
                .within(reporoot)
                .titled(u'Weiterbildung'))

        html = repo.restrictedTraverse('tree').render()

        self.assertIn("1. Weiterbildung", html)
