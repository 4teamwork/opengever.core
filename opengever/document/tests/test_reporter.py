from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.base.actor import Actor
from opengever.testing import create_ogds_user
from opengever.testing import FunctionalTestCase
from openpyxl import load_workbook
from plone.api.portal import get_localized_time
from plone.app.testing import TEST_USER_ID
from tempfile import NamedTemporaryFile


class TestDocumentReporter(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentReporter, self).setUp()
        create_ogds_user('max.mustermann',
                         firstname='Max',
                         lastname='Mustermann')
        self.document_date = date(2020, 02, 01)
        self.receipt_date = date(2020, 02, 02)
        self.delivery_date = date(2020, 02, 03)
        self.dossier = create(Builder('dossier').titled(u'Dossier A'))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .having(
                document_author='max.mustermann',
                document_date=self.document_date,
                receipt_date=self.receipt_date,
                delivery_date=self.delivery_date,
                )
            .checked_out()
            )

    @browsing
    def test_empty_document_report(self, browser):
        browser.login().open(view='document_report',
                             data={'paths:list': []})

        self.assertEquals('Error You have not selected any Items',
                          browser.css('.portalMessage.error').text[0])

    @browsing
    def test_document_report(self, browser):
        browser.login().open(view='document_report',
                             data={'paths:list': [
                                   '/'.join(self.document.getPhysicalPath()),
                                   ]})

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        self.assertSequenceEqual(
            [
             u'Client1 / 1 / 1',
             1L,
             u'Testdokum\xe4nt',
             u'Mustermann Max',
             get_localized_time(self.document_date),
             get_localized_time(self.receipt_date),
             get_localized_time(self.delivery_date),
             Actor.lookup(TEST_USER_ID).get_label(),
             u'unchecked',
             u'Dossier A',
             ],
            [cell.value for cell in list(workbook.active.rows)[1]])
