from ftw.testbrowser import browsing
from opengever.base.interfaces import IWhiteLabelingSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestWhiteLabelingSettingsGet(IntegrationTestCase):

    @browsing
    def test_white_labeling_settings(self, browser):
        browser.open(self.portal, view='/@white-labeling-settings', headers=self.api_headers)

        self.assertIn(u'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJoAAAAeCA',
                      browser.json['logo']['src'])

        api.portal.set_registry_record(
            'logo_src',
            '\x47\x65\x76\x65\x72\x20\x69\x73\x74\x20\x63\x6f\x6f\x6c',
            interface=IWhiteLabelingSettings)

        browser.open(self.portal, view='/@white-labeling-settings', headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@white-labeling-settings',
             u'custom_support_markup':
             {u'de': u'<div>Kundensupport</div>', u'en': None, u'fr': None},
             u'logo': {u'src': u'data:image/png;base64,R2V2ZXIgaXN0IGNvb2w='},
                u'show_created_by': True,
                u'themes': {u'light': {u'primary': u'#d000ff'}}},
            browser.json)
