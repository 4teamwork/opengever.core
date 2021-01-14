from ftw.testbrowser import browsing
from opengever.base.interfaces import IWhiteLabelingSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestWhiteLabelingSettingsGet(IntegrationTestCase):

    @browsing
    def test_white_labeling_settings(self, browser):
        browser.open(self.portal, view='/@white-labeling-settings', headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@white-labeling-settings',
             u'custom_support_markup': {u'de': None, u'en': None, u'fr': None},
             u'logo': {u'src': None},
                u'show_created_by': True,
                u'themes': {u'light': {}}},
            browser.json)

        api.portal.set_registry_record(
            'color_scheme_light', u'{"primary": "#55ff00", "appbarcolor": "#e301f2"}',
            interface=IWhiteLabelingSettings)

        api.portal.set_registry_record(
            'logo_src',
            '\x47\x65\x76\x65\x72\x20\x69\x73\x74\x20\x63\x6f\x6f\x6c',
            interface=IWhiteLabelingSettings)

        browser.open(self.portal, view='/@white-labeling-settings',
                     headers=self.api_headers)
        self.assertEqual({u'appbarcolor': u'#e301f2', u'primary': u'#55ff00'},
                         browser.json['themes']['light'])
        self.assertEqual(u'data:image/png;base64,R2V2ZXIgaXN0IGNvb2w=', browser.json['logo']['src'])
