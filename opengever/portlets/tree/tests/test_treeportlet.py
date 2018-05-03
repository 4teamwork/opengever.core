from ftw.testbrowser import browsing
from opengever.portlets.tree import treeportlet
from opengever.testing import IntegrationTestCase
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestTreePortlet(IntegrationTestCase):

    features = ('favorites', )

    def setUp(self):
        super(TestTreePortlet, self).setUp()
        with self.login(self.administrator):
            self.add_treeportlet(self.repository_root, self.repository_root)

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

    @browsing
    def test_context_url_data_object_is_absolute_url_of_current_context(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        self.assertEqual(
            self.dossier.absolute_url(),
            browser.css('.portletTreePortlet').first.get('data-context-url'))

        browser.open(self.branch_repofolder)
        self.assertEquals(
            self.branch_repofolder.absolute_url(),
            browser.css('.portletTreePortlet').first.get('data-context-url'))

    @browsing
    def test_favorite_tab_is_not_rendered_when_favorites_are_disabled(self, browser):
        self.deactivate_feature('favorites')
        self.login(self.regular_user, browser)
        browser.open(self.dossier)

        self.assertEquals(
            ['Ordnungssystem'],
            browser.css('.portletTreePortlet .portlet-header-tabs li').text)

    @browsing
    def test_favorite_tab_is_rendered_when_favorites_are_enabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        self.assertEquals(
            ['Ordnungssystem', 'Favorites'],
            browser.css('.portletTreePortlet .portlet-header-tabs li').text)
