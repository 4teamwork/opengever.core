from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.filing import IFilingNumber
import transaction


class TestDossierBylineBase(TestBylineBase):
    """Base Test for the dossier byline.
    """


class TestDossierByline(TestDossierBylineBase):

    def create_dossier(self):
        return create(Builder('dossier')
                      .in_state('dossier-state-active')
                      .having(reference_number_prefix='5',
                              responsible='hugo.boss',
                              start=date(2013, 11, 6),
                              end=date(2013, 11, 7),
                              external_reference='22900-2017'))

    @browsing
    def test_dossier_byline_responsible_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        responsible = self.get_byline_value_by_label('Responsible:')
        self.assertEquals('Ziegler Robert (robert.ziegler)', responsible.text)

    @browsing
    def test_dossier_byline_responsible_is_linked_to_user_details(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        responsible = self.get_byline_value_by_label('Responsible:')
        self.assertEqual('http://nohost/plone/@@user-details/robert.ziegler',
                         responsible.get('href'))

    @browsing
    def test_dossier_byline_state_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        state = self.get_byline_value_by_label('State:')
        self.assertEquals('dossier-state-active', state.text)

    @browsing
    def test_dossier_byline_start_date_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Jan 01, 2016', start_date.text)

    @browsing
    def test_dossier_byline_sequence_number_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text)

    @browsing
    def test_dossier_byline_reference_number_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('Client1 1.1 / 1', ref_number.text)

    @browsing
    def test_dossier_byline_email_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        mail_to_link = self.get_byline_value_by_label('E-Mail:')
        self.assertEquals('1014013300@example.org', mail_to_link.text)
        self.assertEquals(
            'mailto:1014013300@example.org', mail_to_link.get('href'))

    @browsing
    def test_dossier_byline_hide_filing_number(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        self.assertEquals(None,
                          self.get_byline_value_by_label('Filing Number:'))

    @browsing
    def test_dossier_byline_external_reference_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        external_reference = self.get_byline_value_by_label(
                'External Reference:')
        self.assertEquals(u'qpr-900-9001-\xf7', external_reference.text)

    @browsing
    def test_dossier_byline_external_reference_link_only_for_valid_url(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        valid_url = "http://google.ch"
        invalid_url = "google.ch"

        IDossier(self.dossier).external_reference = invalid_url
        transaction.commit()
        browser.login().open(self.dossier)
        external_reference = self.get_byline_value_by_label(
                'External Reference:')
        self.assertIsNone(external_reference.node.find("a"))

        IDossier(self.dossier).external_reference = valid_url
        transaction.commit()
        browser.login().open(self.dossier)
        external_reference = self.get_byline_value_by_label(
                'External Reference:')
        self.assertEquals(valid_url, external_reference.node.find("a").get("href"))


class TestFilingBusinessCaseByline(TestBylineBase):

    features = ('filing_number', )

    @browsing
    def test_dossier_byline_filing_number_display(self, browser):
        self.login(self.regular_user, browser=browser)
        IFilingNumber(self.dossier).filing_no = 'OG-Amt-2013-5'

        browser.open(self.dossier)

        filing_number = self.get_byline_value_by_label('Filing Number:')
        self.assertEquals('OG-Amt-2013-5', filing_number.text)
