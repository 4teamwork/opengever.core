from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.mail.mail import get_author_by_email
from opengever.mail.tests import MAIL_DATA
from opengever.mail.tests.utils import get_header_date
from opengever.testing import FunctionalTestCase


def date_format_helper(dateobj):
    """zope.schema.Date default date format"""
    return dateobj.strftime('%d.%m.%Y')


class TestOverview(FunctionalTestCase):
    """Test the overview view of uploaded emails."""

    expected_original_msg_label = 'Raw *.msg message before conversion'
    expected_message_source_label = 'Message source'

    @browsing
    def test_mail_overview_tab(self, browser):
        mail = create(Builder('mail')
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))
        browser.login().visit(mail, view='tabbedview_view-overview')

        expect = [['Document Date', date_format_helper(get_header_date(mail))],
                  ['Document Type', ''],
                  ['Author', get_author_by_email(mail)],
                  ['creator', 'Test User (test_user_1_)'],
                  ['Description', ''],
                  ['Foreign Reference', ''],
                  ['Message',
                   u'Mehrere Anhaenge.eml \u2014 32 KB '
                   u'Checkout and edit Download copy Attach to email'],
                  ['Attachments',
                   'Inneres Testma?il ohne Attachments.eml 1 KB '
                   'word_document.docx 22.4 KB '
                   'Text.txt 1 KB '
                   'Save attachments'],
                  ['Digital Available', 'yes'],
                  ['Preserved as paper', 'yes'],
                  ['Date of receipt', date_format_helper(date.today())],
                  ['Date of delivery', ''],
                  ['Classification', 'unprotected'],
                  ['Privacy layer', 'privacy_layer_no'],
                  ['Public Trial', 'unchecked'],
                  ['Public trial statement', '']]

        self.assertEquals(expect,
                          browser.css('table').first.lists())

    @browsing
    def test_origial_message_info_is_omitted_for_non_managers(self, browser):
        mail = create(Builder('mail')
                      .with_message(MAIL_DATA)
                      .with_dummy_message()
                      .with_dummy_original_message())
        browser.login().visit(mail, view='tabbedview_view-overview')

        by_label = dict(browser.css('table').first.lists())
        self.assertNotIn(self.expected_original_msg_label, by_label)
        self.assertNotIn(self.expected_message_source_label, by_label)

    @browsing
    def test_original_message_info_is_displayed_for_managers(self, browser):
        self.grant('Manager')
        mail = create(Builder('mail')
                      .with_message(MAIL_DATA)
                      .with_dummy_message()
                      .with_dummy_original_message())

        browser.login().visit(mail, view='tabbedview_view-overview')
        by_label = dict(browser.css('table').first.lists())
        self.assertIn(self.expected_original_msg_label, by_label)
        self.assertIn(self.expected_message_source_label, by_label)
