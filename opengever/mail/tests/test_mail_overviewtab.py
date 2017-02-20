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

    @browsing
    def test_mail_overview_tab(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        browser.login().visit(mail, view='tabbedview_view-overview')

        expect = [['Document Date', date_format_helper(get_header_date(mail))],
                  ['Document Type', ''],
                  ['Author', get_author_by_email(mail)],
                  ['creator', 'Test User (test_user_1_)'],
                  ['Description', ''],
                  ['Foreign Reference', ''],
                  ['Original message', u'die-burgschaft.eml \u2014 1 KB Download copy'],
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
