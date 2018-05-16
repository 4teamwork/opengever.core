from ftw.subsite.interfaces import IFtwSubsiteLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.interfaces import IPlonethemeTeamraumLayer
from plonetheme.teamraum.testing import TEAMRAUMTHEME_FUNCTIONAL_TESTING
from plonetheme.teamraum.testing import THEME_SUBSITE_INTEGRATION_TESTING
from Products.Five.browser import BrowserView
from StringIO import StringIO
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager
import base64
import json
import os


class TestCustomLogo(TestCase):

    layer = TEAMRAUMTHEME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_default_logo(self):
        view = self.portal.restrictedTraverse('customlogo')
        self.assertEqual(view.get_logo(headers=False), '')

    def test_import_export_logo(self):
        imgdata = base64.b64encode(
                    'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
                    '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
                    '\x01\x00\x00\x02\x02D\x01\x00;')
        styles_json = StringIO('{"css.logo": "%s"}' % imgdata)


        self.portal.REQUEST.form = {'form.import': '1',
                                    'import_styles': styles_json}

        panel = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        panel()

        view = self.portal.restrictedTraverse('customlogo')
        # now there should be an image
        blob = view.get_logo(headers=False)

        self.assertEqual(blob.read(), base64.b64decode(imgdata))
        # now export the styles
        self.portal.REQUEST.form = {'form.export': '1'}

        tmp = StringIO(panel())
        tmp_data = tmp.read()
        self.assertIn('css.logo', tmp_data)

        # reset the image
        customstyles_util = CustomStylesUtility(self.portal)
        del customstyles_util.annotations['customstyles']['css.logo']
        self.assertEqual(view.get_logo(headers=False), '')

        # import the styles
        styles_json.seek(0)
        self.portal.REQUEST.form = {'form.import': '1',
                                    'import_styles': styles_json}
        panel = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        panel()

        blob = view.get_logo(headers=False)
        self.assertEqual(blob.read(), base64.b64decode(imgdata))


class TestSubsiteLogoIntegration(TestCase):

    layer = THEME_SUBSITE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _get_viewlet(self, obj, with_subsite=False):

        alsoProvides(obj.REQUEST, IPlonethemeTeamraumLayer)

        if with_subsite:
            alsoProvides(obj.REQUEST, IFtwSubsiteLayer)

        view = BrowserView(obj, obj.REQUEST)
        manager_name = 'plone.portalheader'

        manager = queryMultiAdapter(
            (obj, obj.REQUEST, view),
            IViewletManager,
            manager_name)
        self.failUnless(manager)

        # Set up viewlets
        manager.update()
        name = 'plone.logo'
        return [v for v in manager.viewlets if v.__name__ == name]

    def test_teamraum_default(self):
        viewlet = self._get_viewlet(self.portal)[0]

        logo = '++theme++plonetheme.teamraum/images/logo_teamraum.png'
        img_url = '%s/%s' % (self.portal_url, logo)

        self.assertIn(img_url,
            viewlet.logo_tag)

    def test_teamraum_customlogo(self):
        # Import a logo
        handler = open(os.path.join(os.path.dirname(__file__),
                                    'json_files/image1.json'))
        self.portal.REQUEST.form.update({'form.import': '1',
                                         'import_styles': handler})
        panel = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        panel()


        viewlet = self._get_viewlet(self.portal)[0]

        img_url = '%s/customlogo' % self.portal_url

        self.assertIn(img_url,
            viewlet.logo_tag)

    def test_subsite_integration(self):
        subsite = self.portal.get(
            self.portal.invokeFactory('Subsite', 'subsite'))

        #Upload logo
        handler = open(os.path.join(os.path.dirname(__file__),
                                    'json_files/image1.json'))
        styles = json.loads(handler.read())
        logo = StringIO(base64.b64decode(styles['css.logo']))
        subsite.setLogo(logo)

        viewlet = self._get_viewlet(subsite, with_subsite=True)[0]

        # Subsite uses plone.app.imaging
        self.assertIn('@@images', viewlet.logo_tag)
        self.assertIn('title="subsite"', viewlet.logo_tag)

        # Plone root - default
        viewlet = self._get_viewlet(self.portal, with_subsite=True)[0]
        self.assertNotIn('@@images', viewlet.logo_tag)
