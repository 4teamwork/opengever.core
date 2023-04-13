from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.interfaces import IDocPropertyProvider
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.document.docprops import DocPropertyCollector
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.tests import EXPECTED_DOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_DOCUMENT_PROPERTIES
from opengever.dossier.tests import EXPECTED_DOSSIER_PROPERTIES
from opengever.dossier.tests import EXPECTED_PROPOSALDOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_TASKDOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_USER_DOC_PROPERTIES
from opengever.propertysheets.utils import set_custom_property
from opengever.testing import IntegrationTestCase
from zope.component import getAdapter
import json


class TestDocProperties(IntegrationTestCase):

    maxDiff = None

    def test_default_doc_properties_adapter(self):
        self.login(self.regular_user)

        all_properties = DocPropertyCollector(self.document).get_properties()
        self.assertEqual(EXPECTED_DOC_PROPERTIES, all_properties)

    def test_default_doc_properties_adapter_for_taskdocument(self):
        self.login(self.regular_user)

        all_properties = DocPropertyCollector(self.taskdocument).get_properties()
        self.assertEqual(EXPECTED_TASKDOC_PROPERTIES, all_properties)

    def test_default_doc_properties_adapter_for_proposaldocument(self):
        self.login(self.regular_user)

        all_properties = DocPropertyCollector(self.proposaldocument).get_properties()
        self.assertEqual(EXPECTED_PROPOSALDOC_PROPERTIES, all_properties)

    def test_default_document_doc_properties_provider(self):
        self.login(self.regular_user)

        document_adapter = getAdapter(self.document, IDocPropertyProvider)
        self.assertEqual(EXPECTED_DOCUMENT_PROPERTIES,
                         document_adapter.get_properties())

    def test_default_dossier_doc_properties_provider(self):
        self.login(self.regular_user)

        dossier_adapter = getAdapter(self.dossier, IDocPropertyProvider)
        self.assertEqual(EXPECTED_DOSSIER_PROPERTIES,
                         dossier_adapter.get_properties())

    def test_default_member_doc_properties_provider(self):
        self.login(self.regular_user)

        member_adapter = getAdapter(self.regular_user, IDocPropertyProvider)
        self.assertEqual(EXPECTED_USER_DOC_PROPERTIES,
                         member_adapter.get_properties())

    @browsing
    def test_doc_properties_for_dossier_with_custom_fields(self, browser):
        COLORS = [u"Rot", u"Gr\xfcn", u"Blau"]
        LABELS = [u"Alpha", u"Beta", u"Gamma", u"Delta"]

        self.login(self.manager, browser)

        patch_data = {
            "fields": [
                {
                    "name": "location",
                    "field_type": u"textline",
                    "available_as_docproperty": True,
                },
                {
                    "name": "additional_title",
                    "field_type": u"textline",
                    "available_as_docproperty": False,
                },
            ],
        }

        # Patch existing propertysheet
        browser.open(
            view="@propertysheets/dossier_default",
            method="PATCH",
            data=json.dumps(patch_data),
            headers=self.api_headers,
        )

        create(
            Builder("property_sheet_schema")
            .named("businesscase_dossier_schema")
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("choice", u"color", u"Color", u"", False, values=COLORS,
                        available_as_docproperty=True)
            .with_field("bool", u"digital", u"Digital", u"", False, available_as_docproperty=True)
            .with_field("bool", u"checked", u"Checked", u"", False, available_as_docproperty=False)
            .with_field("multiple_choice", u"labels", u"Labels", u"", False, values=LABELS,
                        available_as_docproperty=True)
            .with_field("int", u"age", u"Age", u"", False, available_as_docproperty=True)
            .with_field("int", u"quantity", u"Quantity", u"", False, available_as_docproperty=False)
            .with_field("text", u"note", u"Note", u"", False, available_as_docproperty=True)
            .with_field("textline", u"short_note", u"Short Note", u"", False,
                        available_as_docproperty=True)
            .with_field("date", u"birthday", u"Birthday", u"", False, available_as_docproperty=True)
        )

        IDossierCustomProperties(self.dossier).custom_properties = {
            "IDossier.dossier_type.businesscase": {
                "color": "Gr\xfcn", "digital": False, "checked": True,
                "labels": {u"Alpha", u"Gamma"}, "age": 23, "quantity": 12,
                "note": u"Hi,\nwhat's up?", "short_note": "Hi",
                "birthday": date(1991, 10, 10)},
            "IDossier.default": {"location": u"Bern", "additional_title": "customtitle"},
        }
        expected_properties = {'ogg.dossier.cp.location': u'Bern'}
        expected_properties.update(EXPECTED_DOSSIER_PROPERTIES)

        dossier_adapter = getAdapter(self.dossier, IDocPropertyProvider)
        self.assertEqual(expected_properties,
                         dossier_adapter.get_properties())

        IDossier(self.dossier).dossier_type = u"businesscase"
        expected_properties.update({
            'ogg.dossier.cp.age': 23, 'ogg.dossier.cp.birthday': datetime(1991, 10, 10, 0, 0),
            'ogg.dossier.cp.color': 'Gr\xfcn', 'ogg.dossier.cp.digital': False,
            'ogg.dossier.cp.labels': u'Alpha, Gamma', 'ogg.dossier.cp.note': "Hi, what's up?",
            'ogg.dossier.cp.short_note': 'Hi'})

        self.assertEqual(expected_properties,
                         dossier_adapter.get_properties())

        # handle lists correctly
        set_custom_property(self.dossier, 'labels', value=['Gamma'])
        self.assertEqual(
            u'Gamma',
            dossier_adapter.get_properties().get('ogg.dossier.cp.labels'))

    @browsing
    def test_doc_properties_for_document_with_custom_fields(self, browser):
        COLORS = [u"Rot", u"Gr\xfcn", u"Blau"]
        LABELS = [u"Alpha", u"Beta", u"Gamma", u"Delta"]

        self.login(self.manager, browser)

        patch_data = {
            "fields": [
                {
                    "name": "textline",
                    "field_type": u"textline",
                    "available_as_docproperty": True,
                },
            ],
        }

        # Patch existing propertysheet for document_type regulations
        browser.open(
            view="@propertysheets/schema2",
            method="PATCH",
            data=json.dumps(patch_data),
            headers=self.api_headers,
        )

        create(
            Builder("property_sheet_schema")
            .named("contract_document_schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_field("choice", u"color", u"Color", u"", False, values=COLORS,
                        available_as_docproperty=True)
            .with_field("bool", u"digital", u"Digital", u"", False, available_as_docproperty=True)
            .with_field("bool", u"checked", u"Checked", u"", False, available_as_docproperty=False)
            .with_field("multiple_choice", u"labels", u"Labels", u"", False, values=LABELS,
                        available_as_docproperty=True)
            .with_field("int", u"age", u"Age", u"", False, available_as_docproperty=True)
            .with_field("int", u"quantity", u"Quantity", u"", False, available_as_docproperty=False)
            .with_field("text", u"note", u"Note", u"", False, available_as_docproperty=True)
            .with_field("textline", u"short_note", u"Short Note", u"", False,
                        available_as_docproperty=True)
            .with_field("date", u"birthday", u"Birthday", u"", False, available_as_docproperty=True)
        )

        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.contract": {
                "color": "Gr\xfcn", "digital": False, "checked": True,
                "labels": {u"Alpha", u"Gamma"}, "age": 23, "quantity": 12,
                "note": u"Hi,\nwhat's up?", "short_note": "Hi",
                "birthday": date(1991, 10, 10)},
            "IDocumentMetadata.document_type.regulations": {"textline": u"Hi"},
        }

        expected_properties = {
            'ogg.document.cp.age': 23, 'ogg.document.cp.birthday': datetime(1991, 10, 10, 0, 0),
            'ogg.document.cp.color': 'Gr\xfcn', 'ogg.document.cp.digital': False,
            'ogg.document.cp.labels': u'Alpha, Gamma', 'ogg.document.cp.note': "Hi, what's up?",
            'ogg.document.cp.short_note': 'Hi'}
        expected_properties.update(EXPECTED_DOCUMENT_PROPERTIES)

        document_adapter = getAdapter(self.document, IDocPropertyProvider)
        self.assertEqual(expected_properties,
                         document_adapter.get_properties())
