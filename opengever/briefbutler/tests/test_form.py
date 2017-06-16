from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages import z3cform
from opengever.testing import FunctionalTestCase


class TestForm(FunctionalTestCase):

    def setUp(self):
        super(TestForm, self).setUp()

        self.text_document = create(
            Builder("document")
            .titled(u'A text letter for you')
            .attach_file_containing(u'bla bla', name=u'test.txt'))

        self.pdf_document = create(
            Builder("document")
            .titled(u'A pdf letter for you')
            .attach_file_containing(u'bla bla', name=u'test.pdf'))

    @browsing
    def test_error_message_for_unsupported_content_type(self, browser):
        browser.login().open(self.text_document, view='send_with_briefbutler')
        statusmessages.assert_message(
            'Unsupported content type: BriefButler supports only PDF documents'
        )

    @browsing
    def test_redirect_to_document_view_if_unsupported_content_type(self,
                                                                   browser):
        browser.login().open(self.text_document, view='send_with_briefbutler')
        self.assertEquals(self.text_document.absolute_url(), browser.url)

    @browsing
    def test_no_error_message_for_supported_content_type(self, browser):
        browser.login().open(self.pdf_document, view='send_with_briefbutler')
        statusmessages.assert_no_messages()

    @browsing
    def test_email_validation(self, browser):
        browser.login().open(self.pdf_document, view='send_with_briefbutler')
        browser.fill({'Email': 'peter.meter'})
        browser.find('Send').click()
        statusmessages.assert_message('There were some errors.')
        self.assertIn('Email', z3cform.erroneous_fields(browser.forms['form']))

    @browsing
    def test_main_use_case(self, browser):
        browser.login().open(self.pdf_document, view='send_with_briefbutler')
        browser.fill({
            'Given Name': 'Peter',
            'Family Name': 'Meter',
            'form.widgets.recipient_street': 'Dammweg 9',
            'form.widgets.recipient_door_number': '-',
            'form.widgets.recipient_postal_code': '3013',
            'form.widgets.recipient_city': 'Bern',
            'Email': 'peter.meter@4teamwork.ch',
            'Company Name': '4teamwork',
            'form.widgets.sender_street': 'Dammweg 9',
            'form.widgets.sender_door_number': '-',
            'form.widgets.sender_postal_code': '3013',
            'form.widgets.sender_city': 'Bern',
        })
        browser.find('Send').click()
        statusmessages.assert_message('Document submitted to BriefButler')
