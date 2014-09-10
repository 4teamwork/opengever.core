from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.core.testing import activate_filing_number
from opengever.core.testing import ANNOTATION_LAYER
from opengever.core.testing import inactivate_filing_number
from opengever.dossier.archive import Archiver
from opengever.dossier.archive import default_end_date
from opengever.dossier.archive import EnddateValidator
from opengever.dossier.archive import filing_prefix_default_value
from opengever.dossier.archive import filing_year_default_value
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
from opengever.testing import FunctionalTestCase
from zope.interface import Invalid
from zope.interface.verify import verifyClass


class TestArchiver(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestArchiver, self).setUp()
        activate_filing_number(self.portal)
        self.admin_unit = create(
            Builder('admin_unit').having(title=u'SKA ARCH',
                                         unit_id=u'ska_arch')
                                 .as_current_admin_unit()
        )
        self.user = create(Builder('ogds_user'))
        self.org_unit = create(
            Builder('org_unit').id('client1')
                               .having(title=u'Client1',
                                       admin_unit=self.admin_unit)
                               .as_current_org_unit()
                               .with_default_groups()
                               .assign_users([self.user])
        )

        self.dossier = create(Builder('dossier'))
        self.sub1 = create(Builder('dossier').within(self.dossier))
        self.sub2 = create(Builder('dossier').within(self.dossier))
        self.subsub1 = create(Builder('dossier').within(self.sub1))

        self.archiver = IDossierArchiver(self.dossier)

    def tearDown(self):
        inactivate_filing_number(self.portal)
        super(TestArchiver, self).tearDown()

    def test_number_generation(self):
        self.assertEquals(
            'SKA ARCH-Department-2011-1',
            self.archiver.generate_number('department', '2011'))

        self.assertEquals(
            'SKA ARCH-Department-2011-2',
            self.archiver.generate_number('department', '2011'))

        self.assertEquals(
            'SKA ARCH-Administration-2011-1',
            self.archiver.generate_number('administration', '2011'))

        self.assertEquals(
            'SKA ARCH-Administration-2011-2',
            self.archiver.generate_number('administration', '2011'))

        self.assertEquals(
            'SKA ARCH-Administration-2012-1',
            self.archiver.generate_number('administration', '2012'))

    def test_archiving(self):
        self.archiver.archive('administration', '2013')

        self.assertEquals('SKA ARCH-Administration-2013-1',
                          IFilingNumber(self.dossier).filing_no)
        self.assertEquals('SKA ARCH-Administration-2013-1.1',
                          IFilingNumber(self.sub1).filing_no)
        self.assertEquals('SKA ARCH-Administration-2013-1.2',
                          IFilingNumber(self.sub2).filing_no)
        self.assertEquals('SKA ARCH-Administration-2013-1.1.1',
                          IFilingNumber(self.subsub1).filing_no)

    def test_archiving_with_existing_number(self):
        number = 'FAKE NUMBER'
        self.archiver.archive('administration', '2013', number=number)

        self.assertEquals('FAKE NUMBER',
                          IFilingNumber(self.dossier).filing_no)
        self.assertEquals('FAKE NUMBER.1',
                          IFilingNumber(self.sub1).filing_no)
        self.assertEquals('FAKE NUMBER.2',
                          IFilingNumber(self.sub2).filing_no)
        self.assertEquals('FAKE NUMBER.1.1',
                          IFilingNumber(self.subsub1).filing_no)

    def test_update_prefix(self):
        self.archiver.update_prefix('FAKE PREFIX')

        self.assertEquals('FAKE PREFIX',
                          IDossier(self.dossier).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.sub1).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.sub2).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.subsub1).filing_prefix)


class TestForm(MockTestCase):

    def setUp(self):
        super(TestForm, self).setUp()
        grok('opengever.dossier.archive')

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

    def test_implements_interface(self):
        verifyClass(IDossierArchiver, Archiver)

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

        #dossier not resolved yet without a filing no
        dossier1 = self.stub_dossier()
        self.expect(dossier1.filing_no).result(None)
        self.expect(wft.getInfoFor(dossier1, 'review_state', None)).result(
            'dossier-state-active')

        #dossier not resolved yet with a not valid filing no
        dossier2 = self.stub_dossier()
        self.expect(dossier2.filing_no).result('FAKE_NUMBER')
        self.expect(wft.getInfoFor(dossier2, 'review_state', None)).result(
            'dossier-state-active')

        #dossier not resolved yet with a valid filing no
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

        #dossier not resolved yet but with a filing no
        actions = get_filing_actions(dossier2)
        self.assertEquals(actions.by_token.keys(),
                          [ONLY_RESOLVE, RESOLVE_AND_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING])

        #dossier not resolved yet but with a filing no
        actions = get_filing_actions(dossier3)
        self.assertEquals(
            actions.by_token.keys(),
            [RESOLVE_WITH_EXISTING_NUMBER, RESOLVE_WITH_NEW_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING_EXISTING_FILING])

        # dossier allready resolved but without filing
        actions = get_filing_actions(dossier4)
        self.assertEquals(actions.by_token.keys(),[ONLY_NUMBER])
        self.assertEquals(actions.by_value.keys(),[METHOD_FILING])

    def test_default_prefix(self):
        data = self.stub()
        dossier = self.stub_dossier()
        self.expect(data.context).result(dossier)

        with self.mocker.order():
            self.expect(dossier.filing_prefix).result('administration')
            self.expect(dossier.filing_prefix).result(None)

        self.replay()

        self.assertEquals(filing_prefix_default_value(data), 'administration')
        self.assertEquals(filing_prefix_default_value(data), '')

    def test_default_filing_year(self):
        data = self.stub()
        dossier = self.stub_dossier()
        self.expect(data.context).result(dossier)

        with self.mocker.order():
            self.expect(dossier.earliest_possible_end_date()).result(date(2012, 3, 3))
            self.expect(dossier.earliest_possible_end_date()).result(None)

        self.replay()

        self.assertEquals(filing_year_default_value(data), '2012')
        self.assertEquals(filing_year_default_value(data), None)

    def test_default_end_date(self):
        data = self.stub()
        dossier = self.stub_dossier()
        self.expect(data.context).result(dossier)

        with self.mocker.order():
            self.expect(dossier.end).result(date(2012, 3, 3))
            self.expect(dossier.has_valid_enddate()).result(True)
            self.expect(dossier.end).result(date(2012, 3, 3))

            self.expect(dossier.end).result(None)
            self.expect(dossier.earliest_possible_end_date()).result(date(2012, 4, 4))

            self.expect(dossier.end).result(date(2012, 3, 3))
            self.expect(dossier.has_valid_enddate()).result(True)
            self.expect(dossier.end).result(date(2012, 5, 5))

            self.expect(dossier.filing_year).result(None)

        self.replay()

        self.assertEquals(default_end_date(data), date(2012, 3, 3))
        self.assertEquals(default_end_date(data), date(2012, 4, 4))
        self.assertEquals(default_end_date(data), date(2012, 5, 5))
