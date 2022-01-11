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

    For now, this mainly "documents" what kind of error responses the
    endpoint sends, before unifying them in a next step.
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
                u"message": u'Missing parameter sheet_name.',
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
                u"message": u"The name 'invalid-sheet-id-$$$-xyz' is invalid.",
                u"type": u"BadRequest",
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
                u"message": u"The name 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' "
                            u"is invalid.",
                u"type": u"BadRequest",
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
                u"message": u"The name 'import' is invalid.",
                u"type": u"BadRequest",
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
                u"message": u"The assignment 'slot-that-doesnt-exist' is invalid.",
                u"type": u"BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_rejects_missing_fields(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {"assignments": ["IDossier.default"]}

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

        data = {"assignments": ["IDossier.default"], "fields": []}

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
                u"message": u"[('name', InvalidIdentifier(\"Value 'foo-.$$$' "
                            u"does not match pattern '^[a-z_0-9]*$'\"))]",
                u"type": u"BadRequest",
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
                u"message": u"[('name', ConstraintNotSatisfied('import'))]",
                u"type": u"BadRequest",
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
                u"message": u"[('name', TooLong('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 32))]",
                u"type": u"BadRequest",
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
                u"message": u"Duplicate fields 'myfield'.",
                u"type": u"BadRequest",
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
                u"message": u"[('field_type', ConstraintNotSatisfied('not-a-field-type'))]",
                u"type": u"BadRequest",
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
                u"message": u"[('title', TooLong(u'XXXXXXXXXXXXXXXXXXXXXXXXX"
                            u"XXXXXXXXXXXXXXXXXXXXXXXXX', 48))]",
                u"type": u"BadRequest",
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
                u"message": u"[('description', TooLong(u'%s', 128))]" % ('X' * 130),
                u"type": u"BadRequest",
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
                u"message": u"[('default', WrongType(\"Default value 5.5 of "
                            u"type 'float' not allowed for its field\"))]",
                u"type": u"BadRequest",
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
                u"message": u"[(None, Invalid(\"Invalid default value: u'not-in-vocab'\",))]",
                u"type": u"BadRequest",
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
                u"message": u"[(None, Invalid(\"Invalid default value: u'not-a-number'\",))]",
                u"type": u"BadRequest",
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
                u"message": u"[(None, Invalid('Invalid default value: 42',))]",
                u"type": u"BadRequest",
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
                u"message": u"[(None, Invalid(\"Invalid default value: u'not-a-date'\",))]",
                u"type": u"BadRequest",
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
                u"message": u"[('values', WrongContainedType([WrongType(42, "
                            u"<type 'unicode'>, '')], 'values'))]",
                u"type": u"BadRequest",
            },
            browser.json,
        )
