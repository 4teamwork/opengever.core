from ftw.builder import Builder
from ftw.builder import create
from ftw.solr.interfaces import IFtwSolrLayer
from ftw.testbrowser import browsing
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plonetheme.teamraum.interfaces import IPlonethemeTeamraumLayer
from plonetheme.teamraum.testing import TEAMRAUMTHEME_FUNCTIONAL_TESTING
from plonetheme.teamraum.tests.pages import search_field_placeholder
from Products.Five.browser import BrowserView
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager
import transaction


class TestSeachBoxViewlet(TestCase):

    layer = TEAMRAUMTHEME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _get_viewlet(self, context):
        alsoProvides(context.REQUEST, IPlonethemeTeamraumLayer)

        view = BrowserView(context, context.REQUEST)
        manager_name = 'plone.portalheader'
        manager = queryMultiAdapter(
            (context, context.REQUEST, view),
            IViewletManager,
            manager_name)
        self.failUnless(manager)

        # Set up viewlets
        manager.update()
        name = 'plone.searchbox'
        return [v for v in manager.viewlets if v.__name__ == name][0]

    def test_has_solr_is_false_by_default(self):
        viewlet = self._get_viewlet(self.portal)
        self.assertFalse(viewlet.has_solr())

    def test_when_request_is_marked_with_requestlayer_has_solr_is_false_for_new_solr(self):
        viewlet = self._get_viewlet(self.portal)
        alsoProvides(self.portal.REQUEST, IFtwSolrLayer)

        self.assertFalse(viewlet.has_solr())

    @browsing
    def test_default_plone_placeholder_is_used_by_default(self, browser):
        browser.login().open()
        default_placeholder = translate('title_search_site',
                                        domain='plone',
                                        context=self.request)
        self.assertEquals(default_placeholder,
                          search_field_placeholder())

    @browsing
    def test_customize_placeholder_by_setting_property(self, browser):
        self.portal._setProperty('search_label', 'Search example.com',
                                 'string')
        transaction.commit()
        browser.login().open()
        self.assertEquals('Search example.com',
                          search_field_placeholder())

    @browsing
    def test_customize_placeholder_by_setting_property_with_umlauts(self, browser):
        self.portal._setProperty('search_label', 'R\xc3\xa4ume durchsuchen',
                                 'string')
        transaction.commit()
        browser.login().open()
        self.assertEquals(u'R\xe4ume durchsuchen',
                          search_field_placeholder())

    @browsing
    def test_empty_placeholder_by_setting_property(self, browser):
        self.portal._setProperty('search_label', '', 'string')
        transaction.commit()
        browser.login().open()
        self.assertEquals('', search_field_placeholder())

    @browsing
    def test_placeholder_property_can_be_overriden_on_any_context(self, browser):
        self.portal._setProperty('search_label', 'search portal', 'string')
        folder = create(Builder('folder'))
        folder._setProperty('search_label', 'search folder', 'string')
        transaction.commit()

        placeholders = {}

        browser.login().open()
        placeholders['portal'] = search_field_placeholder()
        browser.open(folder)
        placeholders['folder'] = search_field_placeholder()

        self.assertEquals({'portal': 'search portal',
                           'folder': 'search folder'},
                          placeholders)

    @browsing
    def test_placeholder_property_is_inherited(self, browser):
        self.portal._setProperty('search_label', 'search site', 'string')
        folder = create(Builder('folder'))
        browser.login().open(folder)
        self.assertEquals('search site', search_field_placeholder())
