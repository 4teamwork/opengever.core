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

        # set alternative language to fr
        registry = getUtility(IRegistry)
        reg_proxy = registry.forInterface(IRepositoryFolderRecords)
        reg_proxy.alternative_language_code = u'fr'

    def test_alternative_title_not_enabled_by_default_returns_default_title(self):
        # define tree with primary and alternative title
        reporoot = create(Builder('repository_root')
                .titled(u'Root'))
        repo = create(Builder(u'repository')
                .within(reporoot)
                .titled(u'Weiterbildung'))

        html = repo.restrictedTraverse('tree').render()

        self.assertIn("1. Weiterbildung", html)
