from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import assets
from opengever.testing import IntegrationTestCase


class RedirectorTests(IntegrationTestCase):

    @browsing
    def test_sablon_template_redirector(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.templates, view='++add++opengever.meeting.sablontemplate')
        sablon_template = assets.load('valid_sablon_template.docx')
        browser.fill({
            'Title': u'Sablonv\xferlage',
            'File': (sablon_template, 'valid_sablon_template.docx', 'text/plain'),
        }).save()
        statusmessages.assert_no_error_messages()

        self.assertEquals('http://nohost/plone/vorlagen#sablontemplates-proxy',
                          browser.url)
