from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.dossier.filing.testing import activate_filing_number
from opengever.dossier.filing.testing import inactivate_filing_number
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import transaction


class TestIndexers(FunctionalTestCase):

    def setUp(self):
        super(TestIndexers, self).setUp()
        self.grant('Contributor')

        self.dossier = create(Builder("dossier").titled(u"Testd\xf6ssier XY"))
        self.dossier.reindexObject()

        self.subdossier = create(Builder("dossier")
                                 .within(self.dossier)
                                 .titled(u"Subd\xf6ssier XY"))
        self.subdossier.reindexObject()

        self.document = create(Builder("document").within(self.subdossier))
        self.document.reindexObject()

    def test_containing_dossier(self):
        self.assertEquals(
            obj2brain(self.subdossier).containing_dossier,
            'Testd\xc3\xb6ssier XY')

        self.assertEquals(
            obj2brain(self.document).containing_dossier,
            'Testd\xc3\xb6ssier XY')

        #check subscriber for catch editing maindossier titel
        IOpenGeverBase(self.dossier).title = u"Testd\xf6ssier CHANGED"
        self.dossier.reindexObject()
        notify(
            ObjectModifiedEvent(self.dossier,
                                Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(
            obj2brain(self.subdossier).containing_dossier,
            'Testd\xc3\xb6ssier CHANGED')
        self.assertEquals(
            obj2brain(self.document).containing_dossier,
            'Testd\xc3\xb6ssier CHANGED')

        transaction.commit()

    def test_is_subdossier_index(self):
        self.assertEquals(index_data_for(self.dossier).get('is_subdossier'),
                          False)
        self.assertEquals(index_data_for(self.subdossier).get('is_subdossier'),
                          True)

    def test_containing_subdossier(self):
        self.assertEquals(obj2brain(self.subdossier).containing_subdossier, '')
        self.assertEquals(
            obj2brain(self.document).containing_subdossier,
            'Subd\xc3\xb6ssier XY')

        #check subscriber for catch editing subdossier titel
        IOpenGeverBase(self.subdossier).title = u'Subd\xf6ssier CHANGED'
        self.subdossier.reindexObject()
        notify(
            ObjectModifiedEvent(self.subdossier,
                                Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(
            obj2brain(self.subdossier).containing_subdossier, u'')
        self.assertEquals(
            obj2brain(self.document).containing_subdossier,
            'Subd\xc3\xb6ssier CHANGED')

    def test_filing_no_is_not_indexed_for_default_dossiers(self):
        dossier = create(Builder("dossier")
                         .having(filing_prefix='directorate',
                                 filing_no='SKA ARCH-Administration-2012-3'))

        self.assertEquals(None, index_data_for(dossier).get('filing_no'))
        self.assertEquals(None,
                          index_data_for(dossier).get('searchable_filing_no'))


class TestFilingNumberIndexer(FunctionalTestCase):

    def setUp(self):
        super(TestFilingNumberIndexer, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())
        activate_filing_number(self.portal)

    def tearDown(self):
        super(TestFilingNumberIndexer, self).tearDown()
        inactivate_filing_number(self.portal)

    def test_returns_empty_string_for_dossiers_without_filing_information(self):

        dossier = create(Builder("dossier"))

        # no number, no prefix
        self.assertEquals(None, index_data_for(dossier).get('filing_no'))
        self.assertEquals('',
                          index_data_for(dossier).get('searchable_filing_no'))

    def test_returns_first_part_of_the_filing_number_for_dossiers_with_only_filing_prefix_information(self):
        dossier = create(Builder("dossier")
                 .having(filing_prefix='directorate'))

        self.assertEquals('Client1-Directorate-?',
                          index_data_for(dossier).get('filing_no'))

        self.assertEquals(['client1', 'directorate'],
                          index_data_for(dossier).get('searchable_filing_no'))

    def test_returns_filing_number_for_dossiers_with_only_filing_prefix_information(self):
        dossier = create(Builder("dossier")
                         .having(filing_prefix='directorate',
                                 filing_no='SKA ARCH-Administration-2012-3'))

        # with number and prefix
        self.assertEquals('SKA ARCH-Administration-2012-3',
                          index_data_for(dossier).get('filing_no'))
        self.assertEquals(['ska', 'arch', 'administration', '2012', '3'],
                          index_data_for(dossier).get('searchable_filing_no'))
