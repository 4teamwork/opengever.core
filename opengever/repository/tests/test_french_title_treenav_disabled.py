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

    def test_french_title_not_enabled_by_default_returns_default_title(self):
        # define tree with german and french title
        reporoot = create(Builder('repository_root')
                .titled(u'Root'))
        repo = create(Builder(u'repository')
                .within(reporoot)
                .titled(u'Weiterbildung'))

        html = repo.restrictedTraverse('tree').render()

        self.assertIn("1. Weiterbildung", html)
