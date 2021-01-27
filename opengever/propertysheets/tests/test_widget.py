from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.dexterity import erroneous_fields
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase


class TestPropertySheetWidget(IntegrationTestCase):

    @browsing
    def test_edit_field_rendering_and_submission_all_field_types(
        self, browser
    ):
        self.login(self.manager, browser)

        choices = ["one", "two", "three"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        browser.open(self.document, view="@@edit")

        fieldset = browser.css(
            "#formfield-form-widgets-"
            "IDocumentCustomProperties-custom_properties"
        ).first
        input_labels = fieldset.css(".custom-field label").text
        self.assertEqual(
            [
                u"",  # checkbox labels are rendered next to input
                "Yes or no",
                u"Choose",
                u"Number",
                u"Some lines of text",
                u"A line of text",
            ],
            input_labels,
        )

        browser.fill(
            {
                "Yes or no": True,
                "Choose": "two",
                "Number": "3",
                "Some lines of text": "Foo\nbar",
                "A line of text": u"b\xe4\xe4",
            }
        )
        browser.click_on("Save")
        self.assertEquals(["Changes saved"], info_messages())
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "text": u"Foo\nbar",
                    "num": 3,
                    "yesorno": True,
                    "choose": u"two",
                    "textline": u"b\xe4\xe4",
                }
            },
            IDocumentCustomProperties(self.document).custom_properties,
        )

    @browsing
    def test_add_rendering_and_submission_all_field_types(self, browser):
        self.login(self.manager, browser)

        choices = ["one", "two", "three"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
        )

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view="++add++opengever.document.document")

        # initially no fields for custom properties are rendered as we do not
        # know the document_type yet
        fieldset = browser.css(
            "#formfield-form-widgets-"
            "IDocumentCustomProperties-custom_properties"
        ).first
        input_labels = fieldset.css(".custom-field label").text
        self.assertEqual(0, len(input_labels))

        browser.fill({"Title": "foo", "Document type": "Inquiry"}).save()

        # the initial save will produce errors as we now have a document_type
        # which requires some mandatory custom properties.
        self.assertEqual(["There were some errors."], error_messages())
        errors = erroneous_fields()
        self.assertIn("Custom properties", errors)
        self.assertIn(
            "Custom properties contain some errors.",
            errors["Custom properties"],
        )

        # when we provide the custom properties, saving will succeed
        with self.observe_children(self.dossier) as children:
            browser.fill(
                {
                    "Yes or no": True,
                    "Choose": "two",
                    "Number": "3",
                    "Some lines of text": "Foo\nbar",
                    "A line of text": u"b\xe4\xe4",
                }
            ).save()

        self.assertEqual(1, len(children["added"]))
        document = children["added"].pop()

        self.assertEquals(["Item created"], info_messages())
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "text": u"Foo\nbar",
                    "num": 3,
                    "yesorno": True,
                    "choose": u"two",
                    "textline": u"b\xe4\xe4",
                }
            },
            IDocumentCustomProperties(document).custom_properties,
        )

    @browsing
    def test_edit_required_textline_rendering_and_error_message(self, browser):
        self.login(self.manager, browser)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "textline", u"textline", u"Textline", u"A line of text", True
            )
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        browser.open(self.document, view="@@edit")

        browser.fill({"Textline": None})
        browser.click_on("Save")

        self.assertEqual(["There were some errors."], error_messages())
        # check rendering and chosen id
        field = browser.css(
            "#formfield-custom_property-IDocumentMetadata_document_type_question-textline"
        ).first
        self.assertEqual("Textline", field.css("label").first.raw_text.strip())
        self.assertEqual("A line of text", field.css(".formHelp").first.text)
        # check field error message
        self.assertEqual(
            "Required input is missing.",
            field.css(".fieldErrorBox").first.text,
        )

    @browsing
    def test_edit_required_text_rendering_and_error_message(self, browser):
        self.login(self.manager, browser)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"text", u"Text", u"A lot of text", True)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        browser.open(self.document, view="@@edit")

        browser.fill({"Text": None})
        browser.click_on("Save")

        self.assertEqual(["There were some errors."], error_messages())
        # check rendering and chosen id
        field = browser.css(
            "#formfield-custom_property-IDocumentMetadata_document_type_question-text"
        ).first
        self.assertEqual("Text", field.css("label").first.raw_text.strip())
        self.assertEqual("A lot of text", field.css(".formHelp").first.text)
        # check field error message
        self.assertEqual(
            "Required input is missing.",
            field.css(".fieldErrorBox").first.text,
        )

    @browsing
    def test_edit_required_number_rendering_and_error_message(self, browser):
        self.login(self.manager, browser)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("int", u"num", u"Number", u"A Number", True)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        browser.open(self.document, view="@@edit")

        browser.fill({"Number": None})
        browser.click_on("Save")

        self.assertEqual(["There were some errors."], error_messages())
        # check rendering and chosen id
        field = browser.css(
            "#formfield-custom_property-IDocumentMetadata_document_type_question-num"
        ).first
        self.assertEqual("Number", field.css("label").first.raw_text.strip())
        self.assertEqual("A Number", field.css(".formHelp").first.text)
        # check field error message
        self.assertEqual(
            "Required input is missing.",
            field.css(".fieldErrorBox").first.text,
        )
