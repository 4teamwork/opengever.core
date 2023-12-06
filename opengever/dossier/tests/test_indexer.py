from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.indexers import ParticipationIndexHelper
from opengever.dossier.interfaces import IDossierArchiver
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from plone import api
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent
import json
import requests_mock


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
        self.commit_solr()

        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            solr_data_for(self.subdossier, 'containing_dossier'),
            )

        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            solr_data_for(self.document, 'containing_dossier'),
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
        self.commit_solr()

        self.assertEquals(
            u'Testd\xf6ssier CHANGED',
            solr_data_for(self.subdossier, 'containing_dossier'),
            )

        self.assertEquals(
            u'Testd\xf6ssier CHANGED',
            solr_data_for(self.document, 'containing_dossier'),
            )

    def test_containing_subdossier(self):
        self.login(self.regular_user)

        self.subdossier.reindexObject()
        self.subdocument.reindexObject()
        self.commit_solr()

        self.assertEquals(
            u'',
            solr_data_for(self.subdossier, 'containing_subdossier'),
            )

        self.assertEquals(
            u'2016',
            solr_data_for(self.subdocument, 'containing_subdossier'),
            )

        # Check if the subscribers catch editing the title of a subdossier
        IOpenGeverBase(self.subdossier).title = u'Subd\xf6ssier CHANGED'

        self.subdossier.reindexObject()
        self.subdocument.reindexObject()

        notify(ObjectModifiedEvent(
            self.subdossier,
            Attributes(Interface, 'IOpenGeverBase.title'),
            ))
        self.commit_solr()

        self.assertEquals(
            u'',
            solr_data_for(self.subdossier, 'containing_subdossier'),
            )

        self.assertEquals(
            u'Subd\xf6ssier CHANGED',
            solr_data_for(self.subdocument, 'containing_subdossier'),
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

    def test_dossier_searchable_text_contains_custom_properties_from_default_and_active_slot(self):
        self.login(self.manager)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("text", u"f1", u"Field 1", u"", False)
        )
        IDossier(self.dossier).dossier_type = u"businesscase"
        IDossierCustomProperties(self.dossier).custom_properties = {
            "IDossier.dossier_type.businesscase": {"f1": "indexme-businescase"},
            "IDossier.dossier_type.meeting": {"f1": "noindex-meeting"},
            "IDossier.default": {"additional_title": "indexme-default"},
        }
        self.dossier.reindexObject()
        self.commit_solr()
        indexed_value = solr_data_for(self.dossier, 'SearchableText')

        self.assertIn(u'indexme-businescase', indexed_value)
        self.assertIn(u'indexme-default', indexed_value)
        self.assertNotIn(u'noindex-meeting', indexed_value)

    def test_dossier_searchable_text_with_custom_properties_for_all_field_types(self):
        self.login(self.manager)

        choices = ["rot", u"gr\xfcn", "blau"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field("choice", u"choose", u"Choose", u"", True, values=choices)
            .with_field("multiple_choice", u"choosemulti",
                        u"Choose Multi", u"", True, values=choices)
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
        )
        IDossier(self.dossier).dossier_type = u"businesscase"
        IDossierCustomProperties(self.dossier).custom_properties = {
            "IDossier.dossier_type.businesscase": {
                "yesorno": False,
                "choose": u"gr\xfcn",
                "choosemulti": ["rot", "blau"],
                "num": 122333,
                "text": u"K\xe4fer\nJ\xe4ger",
                "textline": u"Kr\xe4he",
            },
        }
        self.dossier.reindexObject()
        self.commit_solr()
        indexed_value = solr_data_for(self.dossier, 'SearchableText')

        self.assertIn(u"gr\xfcn", indexed_value)
        self.assertIn(u"122333", indexed_value)
        self.assertIn(u"K\xe4fer", indexed_value)
        self.assertIn(u"J\xe4ger", indexed_value)
        self.assertIn(u"Kr\xe4he", indexed_value)
        self.assertIn(u"rot", indexed_value)
        self.assertIn(u"blau", indexed_value)

    def test_dossier_searchable_text_contains_comments(self):
        self.login(self.regular_user)

        response1 = Response(COMMENT_RESPONSE_TYPE)
        response1.text = u'Telefongespr\xe4ch mit Herr Meier'
        IResponseContainer(self.dossier).add(response1)

        response2 = Response(COMMENT_RESPONSE_TYPE)
        response2.text = u'Abschlussnummer DDD2837'
        IResponseContainer(self.dossier).add(response2)

        self.dossier.reindexObject()
        self.commit_solr()

        indexed_value = solr_data_for(self.dossier, 'SearchableText')
        self.assertIn(u'Meier', indexed_value)
        self.assertIn(u'DDD2837', indexed_value)

    @browsing
    def test_searchable_text_gets_updated_when_comment_added(self, browser):
        self.login(self.regular_user, browser=browser)

        indexed_value = solr_data_for(self.dossier, 'SearchableText')
        self.assertNotIn(u'DDD2837', indexed_value)

        url = '{}/@responses'.format(self.dossier.absolute_url())
        browser.open(url, method="POST", headers=self.api_headers,
                     data=json.dumps({'text': u'DDD2837'}))

        self.commit_solr()
        indexed_value = solr_data_for(self.dossier, 'SearchableText')
        self.assertIn(u'DDD2837', indexed_value)

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

    def test_dossier_type_indexer(self):
        self.login(self.regular_user)

        IDossier(self.dossier).dossier_type = None
        self.dossier.reindexObject()
        self.commit_solr()

        self.assertEqual(solr_data_for(self.dossier, 'dossier_type'), None)

        IDossier(self.dossier).dossier_type = "businesscase"
        self.dossier.reindexObject()
        self.commit_solr()
        self.assertEqual(solr_data_for(self.dossier, 'dossier_type'), "businesscase")

    def test_dossiertemplate_dossier_type_indexer(self):
        self.login(self.regular_user)

        IDossierTemplate(self.dossiertemplate).dossier_type = None
        self.dossiertemplate.reindexObject()
        self.commit_solr()

        self.assertEqual(solr_data_for(self.dossiertemplate, 'dossier_type'), None)

        IDossierTemplate(self.dossiertemplate).dossier_type = "businesscase"
        self.dossiertemplate.reindexObject()
        self.commit_solr()
        self.assertEqual(solr_data_for(self.dossiertemplate, 'dossier_type'), "businesscase")


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

    def test_filing_no_is_in_searchable_text_when_dossier_is_archived(self):
        self.login(self.regular_user)

        IDossierArchiver(self.dossier).archive('administration', '2013')
        self.commit_solr()

        expected_filing_no = 'Hauptmandant-Administration-2013-1'
        self.assertEqual(IFilingNumber(self.dossier).filing_no,
                         expected_filing_no)

        indexed_value = solr_data_for(self.dossier, 'SearchableText')
        self.assertIn(expected_filing_no, indexed_value)


class TestDossierParticipationsIndexer(SolrIntegrationTestCase):

    def test_plone_participations_are_indexed_in_solr(self):
        self.login(self.regular_user)

        handler = IParticipationAware(self.dossier)
        handler.add_participation(
            self.regular_user.id, ['participation', 'final-drawing'])

        self.commit_solr()

        indexed_value = solr_data_for(self.dossier, 'participations')
        expected = [
            u'%s|participation' % self.regular_user.id,
            u'%s|final-drawing' % self.regular_user.id,
            u'any-participant|participation',
            u'any-participant|final-drawing',
            u'%s|any-role' % self.regular_user.id]
        self.assertItemsEqual(expected, indexed_value)


@requests_mock.Mocker()
class TestDossierParticipationsIndexerWithKuB(SolrIntegrationTestCase, KuBIntegrationTestCase):

    def test_kub_participations_are_indexed_in_solr(self, mocker):
        self.login(self.regular_user)

        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.person_jean)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(
            self.person_jean, ['participation', 'final-drawing'])

        self.commit_solr()

        indexed_value = solr_data_for(self.dossier, 'participations')
        expected = [
            u'{}|participation'.format(self.person_jean),
            u'{}|final-drawing'.format(self.person_jean),
            u'any-participant|participation',
            u'any-participant|final-drawing',
            u'{}|any-role'.format(self.person_jean)]
        self.assertItemsEqual(expected, indexed_value)


class TestParticipationIndexHelper(IntegrationTestCase):

    def test_participant_id_to_label_handles_invalid_ids(self):
        helper = ParticipationIndexHelper()
        self.assertEqual("Unknown ID", helper.participant_id_to_label("invalid-id"))
