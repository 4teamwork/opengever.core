from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.core.testing import activate_filing_number
from opengever.core.testing import inactivate_filing_number
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

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(
            Builder("dossier")
            .titled(u"Testd\xf6ssier XY")
            .within(self.repo_folder))

        self.subdossier = create(Builder("dossier")
                                 .within(self.dossier)
                                 .titled(u"Subd\xf6ssier XY"))

        self.document = create(Builder("document").within(self.subdossier))

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
        self.assertFalse(index_data_for(self.dossier).get('is_subdossier'))
        self.assertTrue(index_data_for(self.subdossier).get('is_subdossier'))

        dossiertemplate = create(Builder('dossiertemplate'))
        sub_dossiertemplate = create(Builder('dossiertemplate')
                                     .within(dossiertemplate))
        self.assertFalse(index_data_for(dossiertemplate).get('is_subdossier'))
        self.assertTrue(index_data_for(sub_dossiertemplate).get('is_subdossier'))

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

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = self.portal.portal_catalog

        dossier_with_keywords = create(
            Builder("dossier")
            .titled(u"Dossier with keywords")
            .having(keywords=(u'Keyword 1', u'Keyword with \xf6'))
            .within(self.repo_folder))

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')

        create(Builder("dossier")
               .titled(u"Another Dossier with keywords")
               .having(keywords=(u'Keyword 2', ))
               .within(dossier_with_keywords))

        self.assertTrue(len(catalog(Subject=u'Keyword 2')),
                        'Expect one item with Keyword 2')

        self.assertEquals((u'Keyword 1', u'Keyword 2', u'Keyword with \xf6'),
                          catalog.uniqueValuesFor('Subject'))

    def test_dossier_searchable_text_contains_keywords(self):
        dossier_with_keywords = create(
            Builder("dossier")
            .titled(u"Dossier")
            .having(keywords=(u'Pick me!', u'Keyw\xf6rd'))
            .within(self.repo_folder))

        self.assertItemsEqual(
            [u'1', u'3', 'client1', 'dossier', 'keyword', 'me', 'pick'],
            index_data_for(dossier_with_keywords).get('SearchableText'))

    def test_dossier_searchable_text_contains_external_reference(self):
        dossier = create(
            Builder("dossier")
            .titled(u"Dossier")
            .having(external_reference=u'22900-2017')
            .within(self.repo_folder))

        self.assertItemsEqual(
            [u'1', u'3', 'client1', 'dossier', '22900', '2017'],
            index_data_for(dossier).get('SearchableText'))

    def test_dossiertemplate_searchable_text_contains_keywords(self):
        folder = create(Builder('templatefolder'))
        template_with_keywords = create(
            Builder("dossiertemplate")
            .titled(u"Dossiertemplate")
            .having(keywords=(u'Thingy', u'Keyw\xf6rd',))
            .within(folder))

        self.assertItemsEqual(
            [u'1', 'client1', 'dossiertemplate', 'keyword', 'thingy'],
            index_data_for(template_with_keywords).get('SearchableText'))

    def test_external_reference(self):
        dossier = create(
            Builder("dossier")
            .titled(u"Dossier")
            .having(external_reference=u'qpr-900-9001-\xf7')
            .within(self.repo_folder))

        self.assertEquals(
            u'qpr-900-9001-\xf7',
            index_data_for(dossier).get('external_reference'))


class TestFilingNumberIndexer(FunctionalTestCase):

    def setUp(self):
        super(TestFilingNumberIndexer, self).setUp()
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

    def test_filing_no_is_also_in_searchable_text(self):
        dossier = create(Builder("dossier")
                         .having(filing_prefix='directorate',
                                 filing_no='SKA ARCH-Administration-2012-3'))

        searchable_text_data = index_data_for(dossier).get('SearchableText')
        self.assertIn('ska', searchable_text_data)
        self.assertIn('arch', searchable_text_data)
        self.assertIn('administration', searchable_text_data)
        self.assertIn('2012', searchable_text_data)
        self.assertIn('3', searchable_text_data)
