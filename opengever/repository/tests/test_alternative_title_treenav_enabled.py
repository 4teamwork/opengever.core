from Products.CMFCore.utils import getToolByName
from opengever.testing import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.repository.interfaces import IRepositoryFolderRecords
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class TestAlternativeTitleTreenav(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestAlternativeTitleTreenav, self).setUp()
        getToolByName(self.portal, 'portal_languages').setLanguageBindings()

        # enable alternative title
        self.fti = getToolByName(self.portal, 'portal_types').get('opengever.repository.repositoryfolder')
        self.originalBehaviors = self.fti.behaviors
        self.fti.behaviors = self.fti.behaviors + ('opengever.repository.behaviors.alternativetitle.IAlternativeTitleBehavior', )

        # set alternative language to fr
        registry = getUtility(IRegistry)
        reg_proxy = registry.forInterface(IRepositoryFolderRecords)
        reg_proxy.alternative_language_code = u'fr'

    def tearDown(self):
        self.fti.behaviors = self.originalBehaviors

    def test_retuns_alternative_title_if_enabled_and_set(self):
        self.portal.REQUEST.get('LANGUAGE_TOOL').LANGUAGE = 'fr'
        # define tree with german and alternative title
        reporoot = create(Builder('repository_root')
                .titled(u'Root'))
        repo = create(Builder(u'repository')
                .within(reporoot)
                .titled(u'Weiterbildung')
                .having(alternative_title='Formation continue'))

        html = repo.restrictedTraverse('tree').render()

        self.assertIn("1. Formation continue", html)

    def test_retuns_default_title_when_alernative_enabled_but_not_set(self):
        # define tree withOUT alternative title
        reporoot = create(Builder('repository_root')
                .titled(u'Root'))
        repo = create(Builder(u'repository')
                .within(reporoot)
                .titled(u'Weiterbildung'))

        html = repo.restrictedTraverse('tree').render()

        self.assertIn("1. Weiterbildung", html)
