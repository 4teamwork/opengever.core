from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.portlets.tree import treeportlet
from opengever.testing import FunctionalTestCase
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


class TestTreePortlet(FunctionalTestCase):

    def setUp(self):
        super(TestTreePortlet, self).setUp()
        self.repository_root = create(Builder('repository_root')
                                      .titled(u'Repo 1'))
        self.repository = create(Builder('repository')
                                 .within(self.repository_root)
                                 .titled(u'Repository A'))
        self.dossier = create(Builder('dossier')
                              .within(self.repository))

        self.add_treeportlet(self.repository_root, self.repository_root)

        transaction.commit()

    def add_treeportlet(self, context, repository_root):
        manager = getUtility(IPortletManager,
                             name=u'plone.leftcolumn',
                             context=self.portal)
        assignments = getMultiAdapter((context, manager),
                                      IPortletAssignmentMapping,
                                      context=self.portal)

        portlet = treeportlet.Assignment(
            root_path='/'.join(repository_root.getPhysicalPath()))

        name = 'treeportlet_1'
        portlet.__name__ = portlet
        assignments[name] = portlet

    def tearDown(self):
        super(TestTreePortlet, self).tearDown()
        registry = getUtility(IRegistry)
        registry['opengever.portlets.tree.enable_favorites'] = False

    @browsing
    def test_context_url_data_object_is_absolute_url_of_current_context(self, browser):
        browser.login().open(self.dossier)
        self.assertEqual(
            self.dossier.absolute_url(),
            browser.css('.portletTreePortlet').first.get('data-context-url'))

        browser.open(self.repository)
        self.assertEquals(
            self.repository.absolute_url(),
            browser.css('.portletTreePortlet').first.get('data-context-url'))

    @browsing
    def test_favorite_tab_is_not_rendered_when_favorites_are_disabled(self, browser):
        browser.login().open(self.dossier)

        self.assertEquals(
            ['Repo 1'],
            browser.css('.portletTreePortlet .portlet-header-tabs li').text)

    @browsing
    def test_favorite_tab_is_rendered_when_favorites_are_enabled(self, browser):
        registry = getUtility(IRegistry)
        registry['opengever.portlets.tree.enable_favorites'] = True
        transaction.commit()

        browser.login().open(self.dossier)
        self.assertEquals(
            ['Repo 1', 'Favorites'],
            browser.css('.portletTreePortlet .portlet-header-tabs li').text)
