from Products.CMFCore.interfaces import ISiteRoot
from collective.vdexvocabulary.vocabulary import VdexVocabulary
from datetime import date
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from mocker import ANY
from opengever.base.interfaces import IBaseClientID
from opengever.core.testing import ANNOTATION_LAYER
from opengever.dossier.archive import Archiver
from opengever.dossier.archive import EnddateValidator, MissingValue
from opengever.dossier.archive import METHOD_RESOLVING_AND_FILING, METHOD_FILING
from opengever.dossier.archive import METHOD_RESOLVING_EXISTING_FILING
from opengever.dossier.archive import RESOLVE_AND_NUMBER, ONLY_RESOLVE
from opengever.dossier.archive import RESOLVE_WITH_EXISTING_NUMBER, ONLY_NUMBER
from opengever.dossier.archive import RESOLVE_WITH_NEW_NUMBER, METHOD_RESOLVING
from opengever.dossier.archive import filing_year_default_value, default_end_date
from opengever.dossier.archive import get_filing_actions, filing_prefix_default_value
from opengever.dossier.archive import valid_filing_year
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.interfaces import IDossierArchiver
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import provideUtility
from zope.interface import Invalid
from zope.interface.verify import verifyClass
from zope.schema.vocabulary import VocabularyRegistryError
from zope.schema.vocabulary import getVocabularyRegistry
import opengever.dossier
import os


class TestArchiver(MockTestCase):

    layer = ANNOTATION_LAYER

    def setUp(self):
        super(TestArchiver, self).setUp()
        grok('opengever.dossier.archive')
        grok('opengever.dossier.behaviors.filing')

        file_path = os.path.join(
            os.path.dirname(opengever.dossier.__file__),
            'vdexvocabs',
            'type_prefixes.vdex')

        vocabulary_registry = getVocabularyRegistry()
        try:
            vocabulary_registry.get(None, 'opengever.dossier.type_prefixes')
        except VocabularyRegistryError:
            vocabulary_registry.register(
                'opengever.dossier.type_prefixes', VdexVocabulary(file_path))

        proxy = self.mocker.mock()
        proxy.client_id
        self.mocker.result('SKA ARCH')
        self.mocker.count(0, None)

        registry = self.mocker.mock()
        provideUtility(provides=IRegistry, component=registry)
        registry.forInterface(IBaseClientID)
        self.mocker.result(proxy)
        self.mocker.count(0, None)

    def stub_dossier(self):
        return self.providing_stub([IDossier,
                                    IDossierMarker,
                                    IFilingNumber,
                                    IFilingNumberMarker])

    def test_number_generation(self):

        siteroot = self.providing_stub([IAttributeAnnotatable])
        self.mock_utility(siteroot, ISiteRoot)

        dossier = self.providing_stub(
            [IDossier, IDossierMarker])

        self.replay()

        archiver = IDossierArchiver(dossier)

        self.assertEquals(
            archiver.generate_number('department', '2011'),
            'SKA ARCH-Department-2011-1')

        self.assertEquals(
            archiver.generate_number('department', '2011'),
            'SKA ARCH-Department-2011-2')

        self.assertEquals(
            archiver.generate_number('administration', '2011'),
            'SKA ARCH-Administration-2011-1')

        self.assertEquals(
            archiver.generate_number('administration', '2011'),
            'SKA ARCH-Administration-2011-2')

        self.assertEquals(
            archiver.generate_number('administration', '2012'),
            'SKA ARCH-Administration-2012-1')

    def test_archiving(self):
        siteroot = self.providing_stub([IAttributeAnnotatable])
        self.mock_utility(siteroot, ISiteRoot)

        dossier = self.stub_dossier()
        sub1 = self.stub_dossier()
        sub2 = self.stub_dossier()
        subsub1 = self.stub_dossier()

        objs = [dossier, sub1, sub2, subsub1]
        self.expect(dossier.get_subdossiers()).result([sub1, sub2])
        self.expect(sub1.get_subdossiers()).result([subsub1])
        self.expect(subsub1.get_subdossiers()).result([])
        self.expect(sub2.get_subdossiers()).result([])

        for obj in objs:
            self.expect(obj.reindexObject(idxs=ANY))
            self.expect(obj.getObject()).result(obj)

        self.replay()

        archiver = IDossierArchiver(dossier)
        archiver.archive('administration', '2013')

        number = 'SKA ARCH-Administration-2013-1'
        self.assertEquals(dossier.filing_no, number)
        self.assertEquals(sub1.filing_no, 'SKA ARCH-Administration-2013-1.1')
        self.assertEquals(sub2.filing_no, 'SKA ARCH-Administration-2013-1.2')
        self.assertEquals(subsub1.filing_no, 'SKA ARCH-Administration-2013-1.1.1')

    def test_archiving_with_existing_number(self):
        siteroot = self.providing_stub([IAttributeAnnotatable])
        self.mock_utility(siteroot, ISiteRoot)

        dossier = self.stub_dossier()
        sub1 = self.stub_dossier()
        sub2 = self.stub_dossier()
        subsub1 = self.stub_dossier()

        objs = [dossier, sub1, sub2, subsub1]
        self.expect(dossier.get_subdossiers()).result([sub1, sub2])
        self.expect(sub1.get_subdossiers()).result([subsub1])
        self.expect(subsub1.get_subdossiers()).result([])
        self.expect(sub2.get_subdossiers()).result([])

        for obj in objs:
            self.expect(obj.getObject()).result(obj)
            self.expect(obj.reindexObject(idxs=ANY))

        self.replay()

        archiver = IDossierArchiver(dossier)
        number = 'FAKE NUMBER'
        archiver.archive('administration', '2013', number=number)

        self.assertEquals(dossier.filing_no, 'FAKE NUMBER')
        self.assertEquals(sub1.filing_no, 'FAKE NUMBER.1')
        self.assertEquals(sub2.filing_no, 'FAKE NUMBER.2')
        self.assertEquals(subsub1.filing_no, 'FAKE NUMBER.1.1')

    def test_update_prefix(self):
        dossier = self.stub_dossier()
        sub1 = self.stub_dossier()
        sub2 = self.stub_dossier()
        subsub1 = self.stub_dossier()

        objs = [dossier, sub1, sub2, subsub1]
        self.expect(dossier.get_subdossiers()).result([sub1, sub2])
        self.expect(sub1.get_subdossiers()).result([subsub1])
        self.expect(subsub1.get_subdossiers()).result([])
        self.expect(sub2.get_subdossiers()).result([])

        for obj in objs:
            self.expect(obj.getObject()).result(obj)
            self.expect(obj.reindexObject(idxs=ANY))

        self.replay()

        archiver = IDossierArchiver(dossier)
        archiver.update_prefix('FAKE PREFIX')

        self.assertEquals(dossier.filing_prefix, 'FAKE PREFIX')
        self.assertEquals(sub1.filing_prefix, 'FAKE PREFIX')
        self.assertEquals(sub2.filing_prefix, 'FAKE PREFIX')
        self.assertEquals(subsub1.filing_prefix, 'FAKE PREFIX')


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
            'dossier-state-activ')

        #dossier not resolved yet with a not valid filing no
        dossier2 = self.stub_dossier()
        self.expect(dossier2.filing_no).result('FAKE_NUMBER')
        self.expect(wft.getInfoFor(dossier2, 'review_state', None)).result(
            'dossier-state-activ')

        #dossier not resolved yet with a valid filing no
        dossier3 = self.stub_dossier()
        self.expect(dossier3.filing_no).result('TEST A-Amt-2011-2')
        self.expect(wft.getInfoFor(dossier3, 'review_state', None)).result(
            'dossier-state-activ')

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
