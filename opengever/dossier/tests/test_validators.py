from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestStardEndValidator(FunctionalTestCase):

    @browsing
    def test_start_date_must_be_before_end_date(self, browser):
        dossier = create(Builder('dossier')
                         .having(title=u'Testdossier',
                                 responsible=TEST_USER_ID,
                                 start=date(2013, 02, 01),
                                 end=date(2013, 01, 01)))

        browser.login().open(dossier, view='edit')
        browser.click_on('Save')

        self.assertEquals(
            ['Start date must be before end date.'],
            browser.css('div.error').text)

    @browsing
    def test_changing_invalid_dates_on_edit_form_is_possible(self, browser):
        dossier = create(Builder('dossier')
                         .having(title=u'Testdossier',
                                 responsible=TEST_USER_ID,
                                 start=date(2013, 02, 01),
                                 end=date(2013, 01, 01)))

        browser.login().open(dossier, view='edit')
        browser.fill({'End date': '02.02.2013'})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(dossier, browser.context)
