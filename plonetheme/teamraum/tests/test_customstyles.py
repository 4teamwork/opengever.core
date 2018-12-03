from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.importexport import DEFAULT_STYLES
from plonetheme.teamraum.testing import TeamraumThemeTestCase
import json
import os


IMPORT_STYLES = {
    "css.content_background": "#FFFFFF",
    "css.content_width": "80%",
    "css.font_size": "22px",
    "css.footer_background": "#AEAEAE",
    "css.gnav_active_end": "#AA0000",
    "css.gnav_active_start": "#AA0000",
    "css.gnav_bordertop": "#FFAAAA",
    "css.gnav_grad_end": "#AA0000",
    "css.gnav_grad_start": "#FF0000",
    "css.gnav_hover_end": "#00000",
    "css.gnav_hover_start": "#FF0000",
    "css.gnav_shadowtopcolor": "#AAAAAA",
    "css.header_background": "#000000",
    "css.header_height": "260px",
    "css.headerbox_background": "rgba(255,255,255,0.6)",
    "css.headerbox_spacetop": "1em",
    "css.link_color": "#0000FF",
    "css.login_background": "#FFAAAA",
    "css.logo_spaceleft": "true",
    "css.show_fullbanner": "",
    "css.show_headerbox": "on",
    "css.text_color": "#000",
}


class TestCustomStyles(TeamraumThemeTestCase):

    @property
    def style_annotations(self):
        customstyles_util = CustomStylesUtility(self.portal)
        return customstyles_util.annotations

    def test_defaults(self):
        custom_styles = dict(self.style_annotations['customstyles'])
        self.assertTrue(custom_styles.get('css.logo'), 'Missing a logo in the default custom style.')
        del custom_styles['css.logo']
        self.assertEqual(DEFAULT_STYLES, custom_styles)

    def test_update(self):
        self.portal.REQUEST.form.update({'form.submitted': '1',
                                         'css.font_size': '14px'})
        view = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        view()
        self.assertEqual(
            self.style_annotations['customstyles']['css.font_size'], '14px')

    def test_reset(self):
        # default
        view = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        view()
        customstyles_util = CustomStylesUtility(self.portal)
        customstyles_util.save_styles({'css.font_size': '14px'})
        self.assertEqual(
            self.style_annotations['customstyles']['css.font_size'], '14px')
        # reset
        self.portal.REQUEST.form.update({'form.reset': '1'})
        view()
        self.assertEqual(
            self.style_annotations['customstyles']['css.font_size'], '12px')

    def test_export(self):
        view = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        self.portal.REQUEST.form.update({'form.export': '1'})
        custom_styles = json.loads(view())
        self.assertTrue(custom_styles.get('css.logo'), 'Missing a logo in the default custom style.')
        del custom_styles['css.logo']
        self.assertEqual(DEFAULT_STYLES, custom_styles)

    def test_import(self):
        handler = open(os.path.join(os.path.dirname(__file__),
                                    'json_files/styles.json'))

        view = self.portal.restrictedTraverse('teamraumtheme-controlpanel')
        self.portal.REQUEST.form.update({'form.import': '1',
                                         'import_styles': handler})
        view()
        self.assertEqual(dict(
            self.style_annotations['customstyles']), IMPORT_STYLES)

        handler.close()

    def test_dont_add_style_if_value_is_empty(self):
        view = self.portal.restrictedTraverse('customstyles.css')
        view()
        view.css = []

        view.add_style('#h1', {'color': '', 'border': '', 'width': ''})

        self.assertEqual([], view.css)

    def test_add_style_if_value_is_not_empty(self):
        view = self.portal.restrictedTraverse('customstyles.css')
        view()
        view.css = []

        view.add_style('#h1', {'color': 'red', 'border': '', 'width': ''})

        self.assertEqual(['#h1 {\n  color:red;\n}'], view.css)
