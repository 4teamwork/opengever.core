from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.core.testing import ANNOTATION_LAYER
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.archive import Archiver
from opengever.dossier.archive import EnddateValidator
from opengever.dossier.archive import get_filing_actions
from opengever.dossier.archive import METHOD_FILING
from opengever.dossier.archive import METHOD_RESOLVING
from opengever.dossier.archive import METHOD_RESOLVING_AND_FILING
from opengever.dossier.archive import METHOD_RESOLVING_EXISTING_FILING
from opengever.dossier.archive import MissingValue
from opengever.dossier.archive import ONLY_NUMBER
from opengever.dossier.archive import ONLY_RESOLVE
from opengever.dossier.archive import RESOLVE_AND_NUMBER
from opengever.dossier.archive import RESOLVE_WITH_EXISTING_NUMBER
from opengever.dossier.archive import RESOLVE_WITH_NEW_NUMBER
from opengever.dossier.archive import valid_filing_year
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.interfaces import IDossierArchiver
from opengever.testing import IntegrationTestCase
from zope.interface import Invalid
from zope.interface.verify import verifyClass


class TestArchiver(IntegrationTestCase):

    features = ('filing_number', )

    def test_implements_interface(self):
        verifyClass(IDossierArchiver, Archiver)

    def test_number_generation(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            'Hauptmandant-Department-2011-1',
            IDossierArchiver(self.dossier).generate_number('department', '2011'))

        self.assertEquals(
            'Hauptmandant-Department-2011-2',
            IDossierArchiver(self.dossier).generate_number('department', '2011'))

        self.assertEquals(
            'Hauptmandant-Administration-2011-1',
            IDossierArchiver(self.dossier).generate_number('administration', '2011'))

        self.assertEquals(
            'Hauptmandant-Administration-2011-2',
            IDossierArchiver(self.dossier).generate_number('administration', '2011'))

        self.assertEquals(
            'Hauptmandant-Administration-2012-1',
            IDossierArchiver(self.dossier).generate_number('administration', '2012'))

    def test_archiving(self):
        self.login(self.dossier_responsible)
        IDossierArchiver(self.dossier).archive('administration', '2013')

        self.assertEquals('Hauptmandant-Administration-2013-1',
                          IFilingNumber(self.dossier).filing_no)
        self.assertEquals('Hauptmandant-Administration-2013-1.1',
                          IFilingNumber(self.subdossier).filing_no)
        self.assertEquals('Hauptmandant-Administration-2013-1.2',
                          IFilingNumber(self.subdossier2).filing_no)

    def test_archiving_with_existing_number(self):
        self.login(self.dossier_responsible)
        number = 'FAKE NUMBER'
        IDossierArchiver(self.dossier).archive('administration', '2013',
                                               number=number)
        self.assertEquals('FAKE NUMBER',
                          IFilingNumber(self.dossier).filing_no)
        self.assertEquals('FAKE NUMBER.1',
                          IFilingNumber(self.subdossier).filing_no)
        self.assertEquals('FAKE NUMBER.2',
                          IFilingNumber(self.subdossier2).filing_no)

    def test_update_prefix(self):
        self.login(self.dossier_responsible)
        IDossierArchiver(self.dossier).update_prefix('FAKE PREFIX')
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.dossier).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.subdossier).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.subdossier2).filing_prefix)

    def test_valid_filing_year(self):
        self.assertTrue(valid_filing_year(u'2012'))
        self.assertTrue(valid_filing_year('1995'))
        not_valid_years = [
            '-2012', '2012 ', '12.12.2012', 'sdfd', '500', '5000', None]
        for year in not_valid_years:
            with self.assertRaises(Invalid):
                valid_filing_year(year)


class TestArchiving(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(TestArchiving, self).setUp()
        grok('opengever.dossier.archive')

    def stub_dossier(self):
        return self.providing_stub([IDossier,
                                    IDossierMarker,
                                    IFilingNumber,
                                    IFilingNumberMarker])

    def test_end_date_validator(self):

        dossier = self.stub()
        request = self.stub_request()

        self.expect(
            dossier.earliest_possible_end_date()).result(date(2012, 02, 15))
        self.replay()

        from zope.schema.interfaces import IDate
        from zope.interface import Interface
        validator = EnddateValidator(
            dossier, request, Interface, IDate, Interface)

        # invalid
        with self.assertRaises(Invalid):
            validator.validate(date(2012, 02, 10))

        with self.assertRaises(MissingValue):
            self.assertRaises(validator.validate(None))

        # valid
        validator.validate(date(2012, 02, 15))
        validator.validate(date(2012, 04, 15))

    def test_get_filing_actions(self):
        wft = self.stub()
        self.mock_tool(wft, 'portal_workflow')

        # dossier not resolved yet without a filing no
        dossier1 = self.stub_dossier()
        self.expect(dossier1.filing_no).result(None)
        self.expect(wft.getInfoFor(dossier1, 'review_state', None)).result(
            'dossier-state-active')

        # dossier not resolved yet with a not valid filing no
        dossier2 = self.stub_dossier()
        self.expect(dossier2.filing_no).result('FAKE_NUMBER')
        self.expect(wft.getInfoFor(dossier2, 'review_state', None)).result(
            'dossier-state-active')

        # dossier not resolved yet with a valid filing no
        dossier3 = self.stub_dossier()
        self.expect(dossier3.filing_no).result('TEST A-Amt-2011-2')
        self.expect(wft.getInfoFor(dossier3, 'review_state', None)).result(
            'dossier-state-active')

        # dossier allready rsolved no filing
        dossier4 = self.stub_dossier()
        self.expect(dossier4.filing_no).result(None)
        self.expect(wft.getInfoFor(dossier4, 'review_state', None)).result(
            'dossier-state-resolved')

        self.replay()

        # dossier not resolved yet without a filing no
        actions = get_filing_actions(dossier1)
        self.assertEquals(actions.by_token.keys(),
                          [ONLY_RESOLVE, RESOLVE_AND_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING])

        # dossier not resolved yet but with a filing no
        actions = get_filing_actions(dossier2)
        self.assertEquals(actions.by_token.keys(),
                          [ONLY_RESOLVE, RESOLVE_AND_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING])

        # dossier not resolved yet but with a filing no
        actions = get_filing_actions(dossier3)
        self.assertEquals(
            actions.by_token.keys(),
            [RESOLVE_WITH_EXISTING_NUMBER, RESOLVE_WITH_NEW_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING_EXISTING_FILING])

        # dossier allready resolved but without filing
        actions = get_filing_actions(dossier4)
        self.assertEquals(actions.by_token.keys(), [ONLY_NUMBER])
        self.assertEquals(actions.by_value.keys(), [METHOD_FILING])


class TestArchiveFormDefaults(IntegrationTestCase):

    features = ('filing_number', )

    def _get_form_date(self, browser, field_name):
        datestr = browser.css('#form-widgets-%s' % field_name).first.value
        return datetime.strptime(datestr, '%d.%m.%Y').date()

    @browsing
    def test_filing_prefix_default(self, browser):
        # Dossier has no filing_prefix set - default to None in archive form
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_prefix').first.value
        self.assertEqual(None, form_default)

        # Dossier has a filing_prefix - default to that one in archive form
        IDossier(self.dossier).filing_prefix = 'department'
        browser.open(self.dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_prefix').first.value
        self.assertEqual('department', form_default)

    @browsing
    def test_filing_year_default(self, browser):
        self.login(self.dossier_responsible, browser)
        # Dossier without sub-objects - earliest possible end date is dossier
        # start date, filing_year should therefore default to this year
        browser.open(self.dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_year').first.value
        self.assertEqual('2016', form_default)

        # Document with date newer than dossier start. Suggested filing_year
        # default should be that of the document (year of the youngest object)
        doc = create(Builder('document')
                     .within(self.dossier)
                     .having(document_date=date(2050, 1, 1)))
        browser.open(self.dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_year').first.value
        self.assertEqual(doc.document_date.year, int(form_default))

    @browsing
    def test_enddate_may_be_latest_document_date(self, browser):
        """When a document's date is greater than the dossier end date,
        use the document's date.
        """
        self.login(self.dossier_responsible, browser)
        IDossier(self.dossier).end = date(2021, 1, 1)
        self.dossier.reindexObject(idxs=['end'])
        IDocumentMetadata(self.subdocument).document_date = date(2021, 1, 2)
        self.subdocument.reindexObject(idxs=['document_date'])
        browser.open(self.dossier, view='transition-archive')
        self.assertEqual(date(2021, 1, 2),
                         self._get_form_date(browser, 'dossier_enddate'))

    @browsing
    def test_enddate_may_be_latest_dossier_end_date(self, browser):
        """When a dossiers end date is greater than the document's date,
        use the dossier end date.
        """
        self.login(self.dossier_responsible, browser)
        IDossier(self.dossier).end = date(2021, 2, 2)
        self.dossier.reindexObject(idxs=['end'])
        IDocumentMetadata(self.subdocument).document_date = date(2021, 2, 1)
        self.subdocument.reindexObject(idxs=['document_date'])
        browser.open(self.dossier, view='transition-archive')
        self.assertEqual(date(2021, 2, 2),
                         self._get_form_date(browser, 'dossier_enddate'))
