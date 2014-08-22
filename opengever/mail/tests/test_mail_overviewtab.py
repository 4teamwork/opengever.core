from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.mail.mail import get_author_by_email
from opengever.mail.tests.utils import get_header_date
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_string


MAIL_DATA = resource_string('opengever.mail.tests', 'mail.txt')


def date_format_helper(dateobj):
    """zope.schema.Date default date format"""
    return dateobj.strftime('%B %d, %Y').replace(' 0', ' ')


class TestOverview(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestOverview, self).setUp()
        self.grant('Manager')

    @browsing
    def test_mail_overview_tab(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        browser.login().visit(mail, view='tabbedview_view-overview')

        expect = [['Document Date', date_format_helper(get_header_date(mail))],
                  ['Document Type', ''],
                  ['Author', get_author_by_email(mail)],
                  ['creator', '(test_user_1_)'],
                  ['Description', ''],
                  ['Foreign Reference', ''],
                  ['Original message', u'testmail.eml \u2014 1 KB Download copy'],
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
