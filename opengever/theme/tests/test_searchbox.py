from Products.Five.browser import BrowserView
from ftw.builder import Builder
from ftw.builder import create
from ftw.solr.interfaces import IFtwSolrLayer
from ftw.testing.pages import Plone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from opengever.theme.interfaces import IOpengeverThemeLayer
from opengever.theme.testing import GEVERTHEME_FUNCTIONAL_TESTING
from opengever.theme.tests.pages import SearchBox
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager
import transaction


class TestSeachBoxViewlet(TestCase):

    layer = GEVERTHEME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _get_viewlet(self, context):
        alsoProvides(context.REQUEST, IOpengeverThemeLayer)

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

    def test_when_request_is_marked_with_requestlayer_has_solr_is_true(self):
        viewlet = self._get_viewlet(self.portal)
        alsoProvides(self.portal.REQUEST, IFtwSolrLayer)

        self.assertTrue(viewlet.has_solr())

    def test_default_plone_placeholder_is_used_by_deafult(self):
        Plone().visit_portal()
        default_placeholder = translate('title_search_site',
                                        domain='plone',
                                        context=self.request)
        self.assertEquals(default_placeholder,
                          SearchBox().search_field_placeholder)

    def test_customize_placeholder_by_setting_property(self):
        self.portal._setProperty('search_label', 'Search example.com',
                                 'string')
        transaction.commit()
        Plone().visit_portal()
        self.assertEquals('Search example.com',
                          SearchBox().search_field_placeholder)

    def test_customize_placeholder_by_setting_property_with_umlauts(self):
        self.portal._setProperty('search_label', 'R\xc3\xa4ume durchsuchen',
                                 'string')
        transaction.commit()
        Plone().visit_portal()
        self.assertEquals('R\xc3\xa4ume durchsuchen',
                          SearchBox().search_field_placeholder)

    def test_empty_placeholder_by_setting_property(self):
        self.portal._setProperty('search_label', '', 'string')
        transaction.commit()
        Plone().visit_portal()
        self.assertEquals('', SearchBox().search_field_placeholder)

    def test_placeholder_property_can_be_overriden_on_any_context(self):
        self.portal._setProperty('search_label', 'search portal', 'string')
        folder = create(Builder('folder'))
        folder._setProperty('search_label', 'search folder', 'string')
        transaction.commit()

        placeholders = {}

        Plone().login().visit_portal()
        placeholders['portal'] = SearchBox().search_field_placeholder
        Plone().visit(folder)
        placeholders['folder'] = SearchBox().search_field_placeholder

        self.assertEquals({'portal': 'search portal',
                           'folder': 'search folder'},
                          placeholders)

    def test_placeholder_property_is_inherited(self):
        self.portal._setProperty('search_label', 'search site', 'string')
        folder = create(Builder('folder'))
        Plone().login().visit(folder)
        self.assertEquals('search site', SearchBox().search_field_placeholder)
