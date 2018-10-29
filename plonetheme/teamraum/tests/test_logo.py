from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.testing import TeamraumThemeTestCase
from StringIO import StringIO
import base64


class TestCustomLogo(TeamraumThemeTestCase):

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
