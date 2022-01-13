from copy import deepcopy
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json
import transaction
import unittest


class TestSchemaDefinitionPatch(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_patch_assignments(self, browser):
        self.login(self.propertysheets_manager, browser)

        # Create a sheet definition
        data = {
            "fields": [
                {
                    "name": "foo",
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            ],
            "assignments": [u"IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        patch_data = {
            "assignments": [u"IDocumentMetadata.document_type.report"],
        }

        # Patch it
        browser.open(
            view="@propertysheets/question",
            method="PATCH",
            data=json.dumps(patch_data),
            headers=self.api_headers,
        )

        expected = deepcopy(data)
        expected['id'] = 'question'
        expected.update(patch_data)

        self.assertEqual(expected, browser.json)

    @browsing
    def test_patch_fields(self, browser):
        self.login(self.propertysheets_manager, browser)

        # Create a sheet definition
        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein"
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        patch_data = {
            "fields": [
                {
                    "name": "colors",
                    "field_type": u"multiple_choice",
                    "title": u"Some colors",
                    "values": [u"Rot", u"Gr\xfcn", u"Blau"],
                    "description": "Select one or more",
                    "required": False,
                },
            ],
        }

        # Patch it
        browser.open(
            view="@propertysheets/question",
            method="PATCH",
            data=json.dumps(patch_data),
            headers=self.api_headers,
        )

        expected = deepcopy(data)
        expected['id'] = 'question'
        expected.update(patch_data)

        self.assertEqual(expected, browser.json)

    @browsing
    def test_patching_id_is_not_allowed(self, browser):
        self.login(self.propertysheets_manager, browser)

        # Create a sheet definition
        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein"
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }

        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        patch_data = {
            "id": "some_new_id",
        }

        # Patch it
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/question",
                method="PATCH",
                data=json.dumps(patch_data),
                headers=self.api_headers,
            )
        self.assertDictContainsSubset(
            {
                u"message": u"The 'id' of an existing sheet must not be changed.",
                u"type": u"BadRequest",
            },
            browser.json,
        )

    @unittest.expectedFailure
    @browsing
    def test_existing_data_preserved_after_patch(self, browser):
        """Test that existing propertysheet field data is preserved after
        "renaming" (deleting and re-adding) a propertysheet field from the
        definition, and manipulating content in between.
        """
        self.login(self.propertysheets_manager, browser)

        # Create an initial sheet definition
        data = {
            "fields": [
                {
                    "name": "color",
                    "field_type": u"choice",
                    "title": u"A color",
                    "values": [u"Rot", u"Gr\xfcn", u"Blau"],
                    "description": "Select one",
                    "default": u"Rot",
                    "required": False,
                },
            ],
            "assignments": ["IDocument.default"],
        }

        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )
        transaction.commit()

        # Create a document
        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier,
                method="POST",
                data=json.dumps({
                    '@type': 'opengever.document.document',
                    'title': 'My document',
                    'custom_properties': {
                        'IDocument.default': {
                            'color': u'Gr\xfcn',
                        }
                    }
                }),
                headers=self.api_headers,
            )
        document = list(children['added'])[0]
        transaction.commit()

        # Verify custom property field data has been written
        browser.open(
            document.absolute_url(),
            headers=self.api_headers,
        )
        self.assertEqual({
            u'IDocument.default': {
                u'color': {
                    u'title': u'Gr\xfcn',
                    u'token': u'Gr\\xfcn',
                },
            }}, browser.json['custom_properties'])

        # "Rename" the field in the definition
        patch_data = {
            "fields": [
                {
                    "name": "temporary_color_field_name",    # <---
                    "field_type": u"choice",
                    "title": u"A color",
                    "values": [u"Rot", u"Gr\xfcn", u"Blau"],
                    "description": "Select one",
                    "default": u"Rot",
                    "required": False,
                },
            ],
        }
        browser.open(
            view="@propertysheets/question",
            method="PATCH",
            data=json.dumps(patch_data),
            headers=self.api_headers,
        )

        transaction.commit()

        # Old data is still there and getting serialized
        # (no token/title any more though, because schema definition is gone)
        browser.open(
            document.absolute_url(),
            headers=self.api_headers,
        )
        self.assertEqual({
            u'IDocument.default': {
                u'color': u'Gr\xfcn'}
            }, browser.json['custom_properties'])

        # Patch the document and write something to the temporary field
        browser.open(
            document.absolute_url(),
            method="PATCH",
            data=json.dumps({
                'custom_properties': {
                    'IDocument.default': {
                        'temporary_color_field_name': u'Blau',
                        }
                    }
                },
            ),
            headers=self.api_headers,
        )
        transaction.commit()

        # Both the old and new field data should still be there
        browser.open(
            document.absolute_url(),
            headers=self.api_headers,
        )
        self.assertEqual({
            u'IDocument.default': {
                u'color': u'Gr\xfcn',
                u'temporary_color_field_name': {
                    u'title': u'Blau',
                    u'token': u'Blau',
                },
            }}, browser.json['custom_properties'])

        transaction.commit()

        # "Rename" the field back to its old name
        patch_data = {
            "fields": [
                {
                    "name": "color",    # <---
                    "field_type": u"choice",
                    "title": u"A color",
                    "values": [u"Rot", u"Gr\xfcn", u"Blau"],
                    "description": "Select one",
                    "default": u"Rot",
                    "required": False,
                },
            ],
        }
        browser.open(
            view="@propertysheets/question",
            method="PATCH",
            data=json.dumps(patch_data),
            headers=self.api_headers,
        )
        transaction.commit()

        # The original field data should now be serialized again, with the
        # temporary field that also being preserved
        browser.open(
            document.absolute_url(),
            headers=self.api_headers,
        )
        self.assertEqual({
            u'IDocument.default': {
                u'color': {
                    u'title': u'Gr\xfcn',
                    u'token': u'Gr\\xfcn',
                },
                u'temporary_color_field_name': u'Blau',
            }}, browser.json['custom_properties'])
