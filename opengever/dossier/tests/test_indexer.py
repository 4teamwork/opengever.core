from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from plone import api
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent


class TestDossierIndexers(SolrIntegrationTestCase):

    def test_sortable_title_indexer_accomodates_padding_for_five_numbers(self):
        self.login(self.regular_user)
        numeric_part = "1 2 3 4 5"
        alphabetic_part = u"".join(["a" for i in range(CONTENT_TITLE_LENGTH
                                                       - len(numeric_part))])
        title = numeric_part + alphabetic_part

        self.dossier.setTitle(title)
        self.dossier.reindexObject(["sortable_title"])

        self.assertEquals(
            '0001 0002 0003 0004 0005' + alphabetic_part,
            index_data_for(self.dossier).get('sortable_title'))

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
            4,
            len(catalog(Subject=u'Vertr\xe4ge')),
            u'Expected three items with Keyword "Vertr\xe4ge"',
            )

        self.subdossier.reindexObject()

        self.assertEquals(
            3,
            len(catalog(Subject=u'Subkeyword')),
            'Expected three item with Keyword "Subkeyword"',
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
                u'Subsubkeyword',
                u'Subsubkeyw\xf6rd',
                u'Vertr\xe4ge',
                u'Wichtig',
                u'secret',
                u'special',
                ),
            catalog.uniqueValuesFor('Subject'),
            )

    def test_dossier_searchable_text_contains_keywords(self):
        self.login(self.regular_user)

        indexed_value = solr_data_for(self.dossier, 'SearchableText')

        self.assertIn(u'Finanzverwaltung', indexed_value)
        self.assertIn(u'Vertr\xe4ge', indexed_value)

    def test_dossier_searchable_text_contains_external_reference(self):
        self.login(self.regular_user)

        indexed_value = solr_data_for(self.dossier, 'SearchableText')

        self.assertIn(u'qpr-900-9001', indexed_value)

    def test_dossiertemplate_searchable_text_contains_keywords(self):
        self.login(self.regular_user)

        indexed_value = solr_data_for(self.dossiertemplate, 'SearchableText')

        self.assertIn(u'secret', indexed_value)
        self.assertIn(u'special', indexed_value)

    def test_external_reference(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assert_index_value(u'qpr-900-9001-\xf7', 'external_reference', self.dossier)

    def test_blocked_local_roles(self):
        self.login(self.regular_user)
        self.dossier.reindexObject()

        self.assert_index_value(False, 'blocked_local_roles', self.dossier)

        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObject()

        self.assert_index_value(True, 'blocked_local_roles', self.dossier)

        self.dossier.__ac_local_roles_block__ = False
        notify(LocalRolesAcquisitionActivated(self.dossier, ))

        self.assert_index_value(False, 'blocked_local_roles', self.dossier)

        self.dossier.__ac_local_roles_block__ = True
        notify(LocalRolesAcquisitionBlocked(self.dossier, ))

        self.assert_index_value(True, 'blocked_local_roles', self.dossier)


class TestDossierFilingNumberIndexer(SolrIntegrationTestCase):

    features = ('filing_number', )

    filing_prefix = 'directorate'
    filing_no = 'SKA ARCH-Administration-2016-11'
    searchable_filing_no = [
        'ska',
        'arch',
        'administration',
        '2016',
        '11',
        ]

    def test_returns_empty_string_for_dossiers_without_filing_information(self):
        self.login(self.regular_user)

        self.dossier.reindexObject()

        self.assertEquals(
            None,
            index_data_for(self.dossier).get('filing_no'),
            )

        self.assert_index_value(u'', 'searchable_filing_no', self.dossier)

    def test_returns_first_part_of_the_filing_number_for_dossiers_with_only_filing_prefix_information(self):
        self.login(self.regular_user)

        IDossier(self.dossier).filing_prefix = self.filing_prefix
        self.dossier.reindexObject()

        self.assert_index_value(u'Hauptmandant-Directorate-?', 'filing_no', self.dossier)

        self.assertItemsEqual(
            (
                'hauptmandant',
                'directorate',
                ),
            index_data_for(self.dossier).get('searchable_filing_no'),
            )

    def test_returns_filing_number_for_dossiers_with_only_filing_prefix_information(self):
        self.login(self.regular_user)

        IDossier(self.dossier).filing_prefix = self.filing_prefix
        IFilingNumber(self.dossier).filing_no = self.filing_no
        self.dossier.reindexObject()

        self.assert_index_value(self.filing_no, 'filing_no', self.dossier)
        self.assert_index_value(self.searchable_filing_no, 'searchable_filing_no', self.dossier)

    def test_filing_no_is_in_searchable_text(self):
        self.login(self.regular_user)

        IDossier(self.dossier).filing_prefix = self.filing_prefix
        IFilingNumber(self.dossier).filing_no = self.filing_no
        self.dossier.reindexObject()
        self.commit_solr()

        indexed_value = solr_data_for(self.dossier, 'SearchableText')

        self.assertIn('SKA ARCH-Administration-2016-11', indexed_value)
