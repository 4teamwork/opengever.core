from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from io import StringIO
from opengever.testing import IntegrationTestCase
from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.importexport import LOGO_RIGHT_KEY
from plonetheme.teamraum.importexport import LOGO_KEY
import json


CSS_LOGO = u'iVBORw0KGgoAAAANSUhEUgAAAH4AAAAoCAYAAAA49E5iAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBNYWNpbnRvc2giIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6RDlGQ0RCREI4OTAxMTFFOEFGQjJDMTZDRkE0MjMyOTQiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6RDlGQ0RCREM4OTAxMTFFOEFGQjJDMTZDRkE0MjMyOTQiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpEOUZDREJEOTg5MDExMUU4QUZCMkMxNkNGQTQyMzI5NCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpEOUZDREJEQTg5MDExMUU4QUZCMkMxNkNGQTQyMzI5NCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PlG5+DsAAAXQSURBVHja7FrtceJIEAWX/6OLAF0EFnsBWIpgIQLQ/7tatAkYJ3CYugDQRmA2AuQArpAjsBzByhHsTlNvXH3tGX1wWi8201VToBFoZvp1v/6AfvLhz++9lxL9/e8/Wc/Ju5Uzy7zvVOOAd3JCwDt5B/L5j7++qxE64J3UAn/hVNPKs0I1Zke4tdJ249wy750YcHTegN5TNaOu6f2VGmM1cjViNZ9XPILo9FKN9MiOltvytfM3AozPDlDWgND22QTyVo2CDF5dx+r1Vo1rNVZYt3wjepphv7nS0Uazt5q/hRFTiZ6Q/o7e49Wml+plzqZo81GHS5BSVkoZC6xHr5m6vmnpWZcdMc9YrZ3qEKJePsHw7tUYqnuJ5Xtb4EZ7GaihgZ+DiUhnS4zIBnxwpKA3VqBSUFMv9ZmSSIZQcttYGjIG8XgDDIwVakAxt9Xeh/cFvJIkVXNjGOUN9riE0ZtkDtBH4tx7qldzMdak1x3p59ipfi6Uu4KCqkBfA7jGHitCRynjvo79DNgrKLrQSmVrhwgZtM8IQGjgUmFwmlnv8MyUPY+urxkTbSuOMMVnpbE/cX3ByPaOfbTAG+rPhHtMjQc/VsS/DAmcD+XSvR33Wqb4AvMEdp+FhgxGGIrsmT43wvsdDHdhCZ8FPs+9OBFGF7N7X0D7tjO3ynvOq5KeLpOoDsRn8Vdn3p9w6K8Uk+EVNE/l1bPHIGTo5GarridQ1CNTao6Ebp+hq+9FzMN3zBh95pWZ8KRnr1PXK+xvUXEmjxlOxjw2MDBRYQrB2F+vBVZFXQPH68BrPdS4vqHuXRNQGLeIaT2WYElqu8IIRTLzle31GvGaKLMP0H14XgTAKAQs1fsCNFoiC85MP0xphWLNkiu7pm7ewFh9Fia8tmVX0zBl2VNmY5qzDqk5YECuQa0PAGgm4qCeCzH2iQw8s4mMUdZNyNN1HISCH4USx/Cmgnm3z4xRKj2zGL1mQM0aYQ0gBaNhU9J8h+y7Z/hcwZLC/8zVhLimibrXZcvWE0AupQJhDLzDlYoYN4dCC0NypkuSFJ7lVXiQ3FcJlglZXPYrlFZV1Uywh60w1EPCYlBjNIGcs3g2scvHNguf1XSj2naJuLI5KANG1zxZixFLOfhTSuIM9eoj6LjA50so3zfFMMNZdKi4QEgoWpyNZ8Yl9kb7nqn157Kkq3tGje6MYDKG8VgY9RmLzUS49Cxr7pmmM4+31M0JYm0CS+Ug0cYXiOc2OuQbvxRrRVD2TvTJC4MHUwyPMMjYFsyr8gYAvUisEFZS4WmDirhfCMMYSN0Jb15pwwKIMgyuddKJLl2KcEnOQCF2bmEJmnv6mb/Oye6XZ0nWrhoC/4IOwRakoLWIub5QfFXi9NRjP0pVUKpn+S6XmQ4/MEbeXqYkdApPDViOY1wDhhVDP9/AcpwZ7/k1EtcR2CxmeU+fZ/xg00VVHT88AOxSlCiNjcSSGTdhGmKNSzQxMsuzlzXlqde0qgGd6gTwIwDVFBog/GQANhE5yhQglgCIs8WL8IO+hez2PZ+7phF1WB1/YHmRMyv2auJY0rIfXrWfO+a1urzxwQo5gCBW2HfS9L0Wa/MMfIomjgbzhhlYBvA9eN1G0PlIPPemCsif2Up/tc4dFJ4xwyAvvGBNlCHuxayevrNk4c8NJlDrFJSv1ynw/HsoNAFYD2ouRy9gBA/ZGGJzLLwv1YZMJaTlfJmBvbrsZM7+R/XwqsCbqDJhjZeeKO14Bt5EeVtWzm0Ee0wQG4eMAn9neUCsPR73cgPFmsqr125bP8AAPRh+0uLHp4OBDw94Hqf6wBSDiG7hfb4ley4tsV8+6zdd80tgAOakwivfikRMT3lXoJP0Lf+r14rqt7TQBTxNt0Gjqk6fYIXiV3nWKUqnwDt5O3JW48GeU9EJAt87kn/iOHl94J044J04qnfy7oF3yZ2jeienBPzAqcjFeCeO6p044J04qnfiyjknjuqdHKP8EGAAFUb6XRoWQAsAAAAASUVORK5CYII='


class TestCustomStylesImportExport(IntegrationTestCase):

    def file_from_dict(self, educt):
        file_ = StringIO(json.dumps(educt).decode())
        file_.filename = 'customstyles.json'
        file_.content_type = 'application/json'
        return file_

    def get_dict(self):
        return {
            'css.additional_css': u'',
            'css.content_background': u'#FFFFFF',
            'css.content_width': u'90%',
            'css.font_size': u'12px',
            'css.footer_background': u'#f8f8f8',
            'css.footer_height': u'',
            'css.gnav_active_end': u'#3387a1',
            'css.gnav_active_shadowinset': u'#3997b4',
            'css.gnav_active_shadowtop': u'#4a555b',
            'css.gnav_active_start': u'#3387a1',
            'css.gnav_grad_end': u'#4a555b',
            'css.gnav_grad_start': u'#70777d',
            'css.gnav_hover_end': u'#7c848a',
            'css.gnav_hover_shadowinset': u'#787f86',
            'css.gnav_hover_shadowtop': u'#4a555b',
            'css.gnav_hover_start': u'#7c848a',
            'css.gnav_shadowinset': u'#787f86',
            'css.gnav_shadowtop': u'#4a555b',
            'css.header_background': u'#FFFFFF',
            'css.header_height': u'60px',
            'css.headerbox_background': u'rgba(255,255,255,0.6)',
            'css.headerbox_spacetop': u'1em',
            'css.link_color': u'#205C90',
            'css.login_background': u'#3387a1',
            'css.logo': CSS_LOGO,
            'css.logo_right': u'',
            'css.logo_spaceleft': u'on',
            'css.logo_title': u'Gr\xfe\xfe\xfcsige Titu',
            'css.text_color': u'#444',
        }

    @browsing
    def test_import_export_json_without_logo_right_value(self, browser):
        self.login(self.manager, browser)

        data = self.get_dict()
        del data[LOGO_RIGHT_KEY]

        browser.open(self.portal, view='@@teamraumtheme-controlpanel')
        browser.fill({'import_styles': self.file_from_dict(data)})
        browser.find('import styles').click()

        statusmessages.assert_no_error_messages()

        custom_styles = CustomStylesUtility(self.portal)
        self.assertEquals(
            'bschorle',
            custom_styles.annotations['customstyles'].get(LOGO_RIGHT_KEY, 'bschorle'))

        browser.find('export styles').click()
        self.assertEquals(
            data,
            json.loads(browser.contents))

    @browsing
    def test_import_export_json_null_as_logo_right_value(self, browser):
        self.login(self.manager, browser)

        data = self.get_dict()
        data.pop(LOGO_RIGHT_KEY)

        browser.open(self.portal, view='@@teamraumtheme-controlpanel')
        browser.fill({'import_styles': self.file_from_dict(data)})
        browser.find('import styles').click()

        statusmessages.assert_no_error_messages()

        custom_styles = CustomStylesUtility(self.portal)
        self.assertEquals(
            None,
            custom_styles.annotations['customstyles'].get(LOGO_RIGHT_KEY))

        browser.find('export styles').click()
        self.assertEquals(
            data,
            json.loads(browser.contents))

    @browsing
    def test_import_export_json_empty_string_as_logo_right_value(self, browser):
        self.login(self.manager, browser)

        data = self.get_dict()
        data.pop(LOGO_RIGHT_KEY)

        browser.open(self.portal, view='@@teamraumtheme-controlpanel')
        browser.fill({'import_styles': self.file_from_dict(data)})
        browser.find('import styles').click()

        statusmessages.assert_no_error_messages()

        custom_styles = CustomStylesUtility(self.portal)
        self.assertIsNone(
            custom_styles.annotations['customstyles'].get(LOGO_RIGHT_KEY))

        browser.find('export styles').click()
        self.assertEquals(
            data,
            json.loads(browser.contents))

    @browsing
    def test_safe_logo_without_a_right_logo(self, browser):
        self.login(self.manager, browser)

        browser.open(self.portal, view='@@teamraumtheme-controlpanel')
        browser.fill({'Logo': ('Raw file data', 'logo.png', 'image/png')})
        browser.click_on('save')

        self.assertEqual(['Changes saved'], statusmessages.info_messages())

        custom_styles = CustomStylesUtility(self.portal)
        logo = custom_styles.annotations['customstyles'].get(LOGO_KEY)
        self.assertEqual('Raw file data', logo.data)
