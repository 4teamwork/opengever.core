from copy import deepcopy
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestPropertysheetsAPIErrorFormatting(IntegrationTestCase):
    """This test is intended to check the error formatting of the
    @propertysheets endpoint (more so than the actual *handling*).

    This is to make sure that errors are produced in a way where they
    contain enough context, and are in an appropriate format for the
    frontend to render them.
    """

    VALID_SAMPLE_PAYLOAD = {
        "fields": [
            {
                "name": "foo",
                "field_type": "bool",
                "title": u"Y/N",
                "description": u"yes or no",
                "required": True,
            }
        ],
        "assignments": [u"IDossier.default"],
    }

    api_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Language': 'de-ch',
    }

    def post_sheet(self, browser, data, sheet_id='question'):
        browser.open(
            view="@propertysheets/%s" % sheet_id,
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

    @browsing
    def test_rejects_missing_sheet_id(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Must supply exactly one {sheet_id} path parameter.",
                u"type": u"BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_rejects_sheet_id_not_matching_pattern(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            self.post_sheet(browser, data, sheet_id='invalid-sheet-id-$$$-xyz')

        self.assertDictContainsSubset(
            {
                u"type": u"SheetValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"ID:",
                    u"Ung\xfcltiger Bezeichner",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_sheet_id_that_is_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            self.post_sheet(browser, data, sheet_id='x' * 34)

        self.assertDictContainsSubset(
            {
                u"type": u"SheetValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"ID:",
                    u"Wert ist zu lang.",
                    u"(Maximum: 32 Zeichen. Tats\xe4chliche L\xe4nge: 34 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_sheet_id_that_is_a_python_keyword(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            self.post_sheet(browser, data, sheet_id='import')

        self.assertDictContainsSubset(
            {
                u"type": u"SheetValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"ID:",
                    u"Einschr\xe4nkung ist nicht erf\xfcllt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_assignments(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)
        data['assignments'] = [u"slot-that-doesnt-exist"]

        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"AssignmentValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Slots:",
                    u"Falscher Typ f\xfcr Beh\xe4lterinhalt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_assignment_value_type(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)
        data['assignments'] = [42]

        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"AssignmentValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Slots:",
                    u"Falscher Typ f\xfcr Beh\xe4lterinhalt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_assignments_already_in_use(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        # IDossier.default is already used by a fixture object
        data['assignments'] = [u"IDossier.default"]

        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"AssignmentValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Slots:",
                    u"Der Slot 'IDossier.default' ist bereits belegt.",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_missing_fields(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {"assignments": ["IDocument.default"]}

        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"message": u"Missing or invalid field definitions.",
                u"type": u"BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_rejects_empty_fields(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {"assignments": ["IDocument.default"], "fields": []}

        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"message": u"Missing or invalid field definitions.",
                u"type": u"BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_name_not_matching_pattern(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "foo-.$$$",
                    "field_type": "bool",
                    "title": u"Y/N",
                }
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('foo-.$$$'):",
                    u"Parameter 'name': Ung\xfcltiger Bezeichner",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_name_that_is_a_python_keyword(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "import",
                    "field_type": "bool",
                    "title": u"Y/N",
                }
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('import'):",
                    u"Parameter 'name': Einschr\xe4nkung ist nicht erf\xfcllt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_names_that_are_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "x" * 34,
                    "field_type": "bool",
                    "title": u"Y/N",
                }
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'):",
                    u"Parameter 'name': Wert ist zu lang.",
                    u"(Maximum: 32 Zeichen. Tats\xe4chliche L\xe4nge: 34 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_name_duplicates(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"Y/N",
                },
                {
                    "name": "myfield",
                    "field_type": "int",
                    "title": u"Number",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 2 ('myfield'):",
                    u"Parameter 'name': Doppeltes Feld mit diesem Namen",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_type_not_in_vocabulary(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "not-a-field-type",
                    "title": u"My title",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'field_type': Einschr\xe4nkung ist nicht erf\xfcllt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_title_that_is_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"X" * 50,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'title': Wert ist zu lang.",
                    u"(Maximum: 48 Zeichen. Tats\xe4chliche L\xe4nge: 50 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_description_that_is_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"My title",
                    "description": u"X" * 130,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'description': Wert ist zu lang.",
                    u"(Maximum: 128 Zeichen. Tats\xe4chliche L\xe4nge: 130 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_unsupported_types_for_default(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"My title",
                    "default": 5.5,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'default': Objekttyp ist falsch.",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_choice(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"My title",
                    "values": ["alpha", "beta"],
                    "default": "not-in-vocab",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_int(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "int",
                    "title": u"A number",
                    "default": "not-a-number",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_textline(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "textline",
                    "title": u"A line of text",
                    "default": 42,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_date(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "date",
                    "title": u"A date",
                    "default": "not-a-date",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_missing_values_for_choice(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"A choice",
                },
            ],
        }
        with browser.expect_http_error(500):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"message": u"For 'choice' or 'multiple_choice' fields types "
                            u"values are required.",
                u"type": u"InvalidFieldTypeDefinition",
            },
            browser.json,
        )

    @browsing
    def test_rejects_empty_values_for_choice(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"A choice",
                    "values": [],
                },
            ],
        }
        with browser.expect_http_error(500):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"message": u"For 'choice' or 'multiple_choice' fields types "
                            u"values are required.",
                u"type": u"InvalidFieldTypeDefinition",
            },
            browser.json,
        )

    @browsing
    def test_rejects_non_string_term_type_for_values(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"A choice",
                    "values": [42],
                },
            ],
        }
        with browser.expect_http_error(400):
            self.post_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'values': Falscher Typ f\xfcr Beh\xe4lterinhalt",
                ]),
            },
            browser.json,
        )


class TestPropertysheetsAPIErrorFormattingPatch(IntegrationTestCase):
    """Same as above, but for PATCH
    """

    VALID_SAMPLE_PAYLOAD = {
        "fields": [
            {
                "name": "foo",
                "field_type": "bool",
                "title": u"Y/N",
                "description": u"yes or no",
                "required": True,
            }
        ],
        "assignments": [u"IDocumentMetadata.document_type.report"],
    }

    api_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Language': 'de-ch',
    }

    def patch_sheet(self, browser, data, sheet_id='sheet_to_patch', post_first=True):
        if post_first:
            # First create a sheet
            browser.open(
                view="@propertysheets/%s" % sheet_id,
                method="POST",
                data=json.dumps(self.VALID_SAMPLE_PAYLOAD),
                headers=self.api_headers,
            )

        # Then attempt to patch it
        browser.open(
            view="@propertysheets/%s" % sheet_id,
            method="PATCH",
            data=json.dumps(data),
            headers=self.api_headers,
        )

    @browsing
    def test_rejects_missing_sheet_id(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/",
                method="PATCH",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Must supply exactly one {sheet_id} path parameter.",
                u"type": u"BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_rejects_sheet_id_not_matching_pattern(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            self.patch_sheet(
                browser,
                data,
                sheet_id='invalid-sheet-id-$$$-xyz',
                post_first=False,
            )

        self.assertDictContainsSubset(
            {
                u"type": u"SheetValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"ID:",
                    u"Ung\xfcltiger Bezeichner",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_sheet_id_that_is_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            self.patch_sheet(browser, data, sheet_id='x' * 34, post_first=False)

        self.assertDictContainsSubset(
            {
                u"type": u"SheetValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"ID:",
                    u"Wert ist zu lang.",
                    u"(Maximum: 32 Zeichen. Tats\xe4chliche L\xe4nge: 34 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_sheet_id_that_is_a_python_keyword(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        with browser.expect_http_error(400):
            self.patch_sheet(browser, data, sheet_id='import', post_first=False)

        self.assertDictContainsSubset(
            {
                u"type": u"SheetValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"ID:",
                    u"Einschr\xe4nkung ist nicht erf\xfcllt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_assignments(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)
        data['assignments'] = [u"slot-that-doesnt-exist"]

        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"AssignmentValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Slots:",
                    u"Falscher Typ f\xfcr Beh\xe4lterinhalt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_assignment_value_type(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)
        data['assignments'] = [42]

        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"AssignmentValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Slots:",
                    u"Falscher Typ f\xfcr Beh\xe4lterinhalt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_assignments_already_in_use(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = deepcopy(self.VALID_SAMPLE_PAYLOAD)

        # IDossier.default is already used by a fixture object
        data['assignments'] = [u"IDossier.default"]

        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"AssignmentValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Slots:",
                    u"Der Slot 'IDossier.default' ist bereits belegt.",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_allows_missing_fields(self, browser):
        """Rejecting missing fields makes sense for POST,
        but not so much for PATCH.
        """
        self.login(self.propertysheets_manager, browser)

        data = {"assignments": ["IDocument.default"]}

        self.patch_sheet(browser, data)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_allows_empty_fields(self, browser):
        """Rejecting empty fields makes sense for POST,
        but not so much for PATCH.
        """
        self.login(self.propertysheets_manager, browser)

        data = {"assignments": ["IDocument.default"], "fields": []}

        self.patch_sheet(browser, data)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_rejects_field_name_not_matching_pattern(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "foo-.$$$",
                    "field_type": "bool",
                    "title": u"Y/N",
                }
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('foo-.$$$'):",
                    u"Parameter 'name': Ung\xfcltiger Bezeichner",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_name_that_is_a_python_keyword(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "import",
                    "field_type": "bool",
                    "title": u"Y/N",
                }
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('import'):",
                    u"Parameter 'name': Einschr\xe4nkung ist nicht erf\xfcllt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_names_that_are_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "x" * 34,
                    "field_type": "bool",
                    "title": u"Y/N",
                }
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'):",
                    u"Parameter 'name': Wert ist zu lang.",
                    u"(Maximum: 32 Zeichen. Tats\xe4chliche L\xe4nge: 34 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_name_duplicates(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"Y/N",
                },
                {
                    "name": "myfield",
                    "field_type": "int",
                    "title": u"Number",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 2 ('myfield'):",
                    u"Parameter 'name': Doppeltes Feld mit diesem Namen",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_field_type_not_in_vocabulary(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "not-a-field-type",
                    "title": u"My title",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'field_type': Einschr\xe4nkung ist nicht erf\xfcllt",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_title_that_is_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"X" * 50,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'title': Wert ist zu lang.",
                    u"(Maximum: 48 Zeichen. Tats\xe4chliche L\xe4nge: 50 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_description_that_is_too_long(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"My title",
                    "description": u"X" * 130,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'description': Wert ist zu lang.",
                    u"(Maximum: 128 Zeichen. Tats\xe4chliche L\xe4nge: 130 Zeichen)",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_unsupported_types_for_default(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "bool",
                    "title": u"My title",
                    "default": 5.5,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'default': Objekttyp ist falsch.",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_choice(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"My title",
                    "values": ["alpha", "beta"],
                    "default": "not-in-vocab",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_int(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "int",
                    "title": u"A number",
                    "default": "not-a-number",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_textline(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "textline",
                    "title": u"A line of text",
                    "default": 42,
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_invalid_default_value_for_date(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "date",
                    "title": u"A date",
                    "default": "not-a-date",
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Ung\xfcltiger Default-Wert",
                ]),
            },
            browser.json,
        )

    @browsing
    def test_rejects_missing_values_for_choice(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"A choice",
                },
            ],
        }
        with browser.expect_http_error(500):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"message": u"For 'choice' or 'multiple_choice' fields types "
                            u"values are required.",
                u"type": u"InvalidFieldTypeDefinition",
            },
            browser.json,
        )

    @browsing
    def test_rejects_empty_values_for_choice(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"A choice",
                    "values": [],
                },
            ],
        }
        with browser.expect_http_error(500):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"message": u"For 'choice' or 'multiple_choice' fields types "
                            u"values are required.",
                u"type": u"InvalidFieldTypeDefinition",
            },
            browser.json,
        )

    @browsing
    def test_rejects_non_string_term_type_for_values(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "myfield",
                    "field_type": "choice",
                    "title": u"A choice",
                    "values": [42],
                },
            ],
        }
        with browser.expect_http_error(400):
            self.patch_sheet(browser, data)

        self.assertDictContainsSubset(
            {
                u"type": u"FieldValidationError",
                u"translated_message": "\n".join([
                    u"Das Formular enth\xe4lt Fehler:",
                    u"Feld 1 ('myfield'):",
                    u"Parameter 'values': Falscher Typ f\xfcr Beh\xe4lterinhalt",
                ]),
            },
            browser.json,
        )
