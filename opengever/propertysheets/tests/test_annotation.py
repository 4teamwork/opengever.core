from opengever.propertysheets.annotation import CustomPropertiesStorage
from opengever.propertysheets.annotation import CustomPropertiesStorageImpl
from opengever.propertysheets.assignment import DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX
from opengever.propertysheets.exceptions import BadCustomPropertiesFactoryConfiguration
from opengever.propertysheets.field import PropertySheetField
from opengever.testing.test_case import FunctionalTestCase
from persistent.dict import PersistentDict
from plone.supermodel import model
from zope import schema
from zope.annotation.interfaces import IAnnotations


def fixture_assignment_factory():
    return [
        u"IDocumentMetadata.document_type.contract",
        u"IDocumentMetadata.document_type.question",
    ]


class ITestFixtureWithCustomProperties(model.Schema):

    custom_properties = PropertySheetField(
        request_key='some_request_key',
        attribute_name='some_attribute',
        assignemnt_prefix=DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX,
        valid_assignment_slots_factory=fixture_assignment_factory,
    )


class TestCustomPropertiesStorage(FunctionalTestCase):

    def setUp(self):
        super(TestCustomPropertiesStorage, self).setUp()
        self.factory = CustomPropertiesStorage(
            ITestFixtureWithCustomProperties
        )
        # any IAnnotatable will serve as a test-fixture
        self.context = self.portal
        self.props = self.factory(self.context)
        self.annotations = IAnnotations(self.context)
        self.key = (
            'opengever.propertysheets.tests.test_annotation.'
            'ITestFixtureWithCustomProperties.custom_properties'
        )

    def assert_custom_properties_equal(self, expected):
        self.assertEqual(expected, self.props.custom_properties)
        self.assertEqual(expected, self.annotations[self.key])

    def test_custom_property_storage_is_none_per_default(self):
        self.assertIsNone(self.props.custom_properties)

    def test_custom_property_storage_initialzes_none_in_annotations(self):
        self.assertNotIn(self.key, self.annotations)

        self.props.custom_properties = None
        self.assertIn(self.key, self.annotations)
        self.assertIsNone(self.annotations[self.key])

        self.assertIsNone(self.props.custom_properties)

    def test_custom_property_storage_initialzes_empty_dict_in_annotations(self):
        self.assertNotIn(self.key, self.annotations)

        self.props.custom_properties = {}
        self.assertIn(self.key, self.annotations)
        self.assertIsInstance(self.annotations[self.key], PersistentDict)
        self.assertEqual(PersistentDict(), self.annotations[self.key])

    def test_custom_property_storage_raises_attribute_error_for_unknowns(self):
        with self.assertRaises(AttributeError):
            self.props.foo

    def test_custom_property_storage_converts_values_to_persistent(self):
        self.props.custom_properties = {"foo": 123}
        self.assertIsInstance(self.props.custom_properties, PersistentDict)

    def test_custom_property_storage_updates_existing_values(self):
        self.props.custom_properties = {"foo": 123}
        self.props.custom_properties = {"bar": "qux"}

        expected = {"foo": 123, "bar": "qux"}
        self.assert_custom_properties_equal(expected)

    def test_custom_property_storage_keeps_existing_when_set_to_empty(self):
        self.props.custom_properties = {"foo": 123}
        self.props.custom_properties = {}

        expected = {"foo": 123}
        self.assert_custom_properties_equal(expected)

    def test_custom_property_storage_keeps_existing_when_set_to_none(self):
        self.props.custom_properties = {"foo": 123}
        self.props.custom_properties = None

        expected = {"foo": 123}
        self.assert_custom_properties_equal(expected)

    def test_custom_property_storage_allows_clearing(self):
        self.props.custom_properties = {"foo": 123}
        self.assertEqual({"foo": 123}, self.props.custom_properties)

        self.props.clear()
        self.assertIsNone(self.props.custom_properties)
        self.assertNotIn(self.key, self.annotations)

    def test_custom_property_storage_allows_clearing_of_empty_storage(self):
        self.assertIsNone(self.props.custom_properties)

        self.props.clear()
        self.assertIsNone(self.props.custom_properties)
        self.assertNotIn(self.key, self.annotations)

    def test_custom_property_storage_prevents_setting_wrong_iterable_type(self):
        with self.assertRaises(TypeError):
            self.props.custom_properties = []

        with self.assertRaises(TypeError):
            self.props.custom_properties = ['foo']

        with self.assertRaises(TypeError):
            self.props.custom_properties = tuple()

        with self.assertRaises(TypeError):
            self.props.custom_properties = ('foo', 'bar')

    def test_custom_property_storage_prevents_setting_basic_type(self):
        with self.assertRaises(TypeError):
            self.props.custom_properties = 0

        with self.assertRaises(TypeError):
            self.props.custom_properties = ''

        with self.assertRaises(TypeError):
            self.props.custom_properties = 'blub'

        with self.assertRaises(TypeError):
            self.props.custom_properties = 123

        with self.assertRaises(TypeError):
            self.props.custom_properties = 1.3

        with self.assertRaises(TypeError):
            self.props.custom_properties = True

        with self.assertRaises(TypeError):
            self.props.custom_properties = False

    def test_factory_validates_schema_field_name(self):
        class SchemaWithMissingField(model.Schema):
            pass

        context = None
        with self.assertRaises(BadCustomPropertiesFactoryConfiguration) as cm:
            CustomPropertiesStorageImpl(context, SchemaWithMissingField)

        self.assertEqual(
            u"Custom properties factory must be assigned to a "
            u"schema with only a 'custom_properties' field.",
            cm.exception.message
        )

    def test_factory_validates_schema_field_type(self):
        class SchemaWithWrongField(model.Schema):
            custom_properties = schema.Text()

        context = None
        with self.assertRaises(BadCustomPropertiesFactoryConfiguration) as cm:
            CustomPropertiesStorageImpl(context, SchemaWithWrongField)

        self.assertEqual(
            u"The schema must contain a field providing 'IPropertySheetField'",
            cm.exception.message
        )
