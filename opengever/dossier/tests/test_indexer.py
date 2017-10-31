from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.core.testing import activate_filing_number
from opengever.core.testing import inactivate_filing_number
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from plone import api
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent


class TestDossierIndexers(IntegrationTestCase):
    def test_containing_dossier(self):
        self.login(self.regular_user)

        self.subdossier.reindexObject()
        self.subdocument.reindexObject()

        self.assertEquals(
            'Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
            obj2brain(self.subdossier).containing_dossier,
            )

        self.assertEquals(
            'Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
            obj2brain(self.document).containing_dossier,
            )

        # Check if the subscribers catch editing the title of a dossier
        IOpenGeverBase(self.dossier).title = u"Testd\xf6ssier CHANGED"

        self.dossier.reindexObject()
        self.subdossier.reindexObject()
        self.subdocument.reindexObject()

        notify(ObjectModifiedEvent(
            self.dossier,
            Attributes(Interface, 'IOpenGeverBase.title'),
            ))

        self.assertEquals(
            'Testd\xc3\xb6ssier CHANGED',
            obj2brain(self.subdossier).containing_dossier,
            )

        self.assertEquals(
            'Testd\xc3\xb6ssier CHANGED',
            obj2brain(self.document).containing_dossier,
            )

    def test_is_subdossier_index(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()
        self.subdossier.reindexObject()
        self.dossiertemplate.reindexObject()
        self.subdossiertemplate.reindexObject()

        index_name = 'is_subdossier'
        self.assert_index_value(False, index_name, self.dossier)
        self.assert_index_value(False, index_name, self.dossiertemplate)
        self.assert_index_value(True, index_name, self.subdossier)
        self.assert_index_value(True, index_name, self.subdossiertemplate)

    def test_containing_subdossier(self):
        self.login(self.regular_user)

        self.subdossier.reindexObject()
        self.subdocument.reindexObject()

        self.assertEquals(
            '',
            obj2brain(self.subdossier).containing_subdossier,
            )

        self.assertEquals(
            '2016',
            obj2brain(self.subdocument).containing_subdossier,
            )

        # Check if the subscribers catch editing the title of a subdossier
        IOpenGeverBase(self.subdossier).title = u'Subd\xf6ssier CHANGED'

        self.subdossier.reindexObject()
        self.subdocument.reindexObject()

        notify(ObjectModifiedEvent(
            self.subdossier,
            Attributes(Interface, 'IOpenGeverBase.title'),
            ))

        self.assertEquals(
            u'',
            obj2brain(self.subdossier).containing_subdossier,
            )

        self.assertEquals(
            'Subd\xc3\xb6ssier CHANGED',
            obj2brain(self.subdocument).containing_subdossier,
            )

    def test_filing_no_is_not_indexed_for_default_dossiers(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assertEquals(None, index_data_for(self.dossier).get('filing_no'))
        self.assertEquals(None, index_data_for(self.dossier).get('searchable_filing_no'))

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = api.portal.get_tool(name="portal_catalog")

        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assertEquals(
            2,
            len(catalog(Subject=u'Finanzverwaltung')),
            'Expected two items with Keyword "Finanzverwaltung"',
            )

        self.assertEquals(
            3,
            len(catalog(Subject=u'Vertr\xe4ge')),
            u'Expected three items with Keyword "Vertr\xe4ge"',
            )

        self.subdossier.reindexObject()

        self.assertEquals(
            1,
            len(catalog(Subject=u'Subkeyword')),
            'Expected one item with Keyword "Subkeyword"',
            )

        self.assertEquals(
            1,
            len(catalog(Subject=u'Subkeyw\xf6rd')),
            u'Expected one item with Keyword "Subkeyw\xf6rd"',
            )

        self.assertEquals(
            (
                u'Finanzverwaltung',
                u'Subkeyword',
                u'Subkeyw\xf6rd',
                u'Vertr\xe4ge',
                u'secret',
                u'special',
                ),
            catalog.uniqueValuesFor('Subject'),
            )

    def test_dossier_searchable_text_contains_keywords(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assertIn(
            'finanzverwaltung',
            index_data_for(self.dossier).get('SearchableText'),
            )

        self.assertIn(
            'vertrage',
            index_data_for(self.dossier).get('SearchableText'),
            )

    def test_dossier_searchable_text_contains_external_reference(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assertIn(
            'qpr',
            index_data_for(self.dossier).get('SearchableText'),
            )

        self.assertIn(
            u'900',
            index_data_for(self.dossier).get('SearchableText'),
            )

        self.assertIn(
            u'9001',
            index_data_for(self.dossier).get('SearchableText'),
            )

    def test_dossiertemplate_searchable_text_contains_keywords(self):
        self.login(self.regular_user)

        self.dossiertemplate.reindexObject()

        self.assertIn(
            'secret',
            index_data_for(self.dossiertemplate).get('SearchableText'),
        )

        self.assertIn(
            'special',
            index_data_for(self.dossiertemplate).get('SearchableText'),
        )

    def test_external_reference(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assert_index_value(u'qpr-900-9001-\xf7', 'external_reference', self.dossier)


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
        dossier = create(Builder("dossier").having(filing_prefix='directorate'))

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
