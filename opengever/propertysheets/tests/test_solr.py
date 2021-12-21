from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


class TestCustomPropertiesIndexHandler(SolrIntegrationTestCase):

    def test_index_custom_properties_from_default_and_active_slot(self):
        self.login(self.manager)
        create(
            Builder("property_sheet_schema")
            .named("default_doc_schema")
            .assigned_to_slots(u"IDocument.default")
            .with_field("textline", u"f1", u"Field 1", u"", False)
        )
        self.document.document_type = u'directive'
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.directive": {
                "textline": u"indexme-directive",
            },
            "IDocumentMetadata.document_type.regulations": {
                "textline": u"noindex-regulations",
            },
            "IDocument.default": {"f1": "indexme-default"},
        }
        self.document.reindexObject()
        self.commit_solr()

        solr_doc = solr_data_for(self.document)
        self.assertEqual(solr_doc.get(u'f1_custom_field_string'), u'indexme-default')
        self.assertEqual(solr_doc.get(u'textline_custom_field_string'), u'indexme-directive')

    def test_index_custom_properties_with_all_types(self):
        self.login(self.regular_user)

        self.document.document_type = u'regulations'
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.regulations": {
                "yesorno": False,
                "choose": u"gr\xfcn",
                "choosemulti": ["two", "three"],
                "num": 122333,
                "text": u"K\xe4fer\nJ\xe4ger",
                "textline": u"Kr\xe4he",
                "date": date(2021, 12, 21),
            }
        }
        self.document.reindexObject()
        self.commit_solr()

        solr_doc = solr_data_for(self.document)
        self.assertEqual(
            solr_doc.get(u'yesorno_custom_field_boolean'), False)
        self.assertEqual(
            solr_doc.get(u'choose_custom_field_string'), u"gr\xfcn")
        self.assertEqual(
            solr_doc.get(u'choosemulti_custom_field_strings'), ["three", "two"])
        self.assertEqual(
            solr_doc.get(u'num_custom_field_int'), 122333)
        self.assertNotIn(u'text_custom_field_string', solr_doc)
        self.assertEqual(
            solr_doc.get(u'textline_custom_field_string'), u"Kr\xe4he")
        self.assertEqual(
            solr_doc.get(u'date_custom_field_date'), u'2021-12-21T00:00:00Z')

    def test_index_custom_properties_of_dossiers(self):
        self.login(self.manager)

        create(
            Builder("property_sheet_schema")
            .named("businesscase_dossier_schema")
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("textline", u"f1", u"Field 1", u"", False)
        )
        IDossier(self.dossier).dossier_type = u"businesscase"
        IDossierCustomProperties(self.dossier).custom_properties = {
            "IDossier.dossier_type.businesscase": {"f1": "indexme-businesscase"},
            "IDossier.default": {"additional_title": "indexme-default"},
        }
        self.dossier.reindexObject()
        self.commit_solr()

        solr_doc = solr_data_for(self.dossier)
        self.assertEqual(
            solr_doc.get(u'f1_custom_field_string'), u'indexme-businesscase')
        self.assertEqual(
            solr_doc.get(u'additional_title_custom_field_string'), u'indexme-default')
