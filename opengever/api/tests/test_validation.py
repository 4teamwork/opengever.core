from opengever.api.exceptions import UnknownField
from opengever.api.validation import get_validation_errors
from opengever.testing import FunctionalTestCase
from plone.supermodel.model import Schema


class TestSchema(Schema):
    """
    """


class TestSchemaValidation(FunctionalTestCase):

    def test_allow_unknown_fields(self):
        data = {'lorem_ipsum_field': u'james.bond'}

        errors = get_validation_errors(data, TestSchema, allow_unknown_fields=True)
        self.assertEqual([], errors)

        errors = get_validation_errors(data, TestSchema, allow_unknown_fields=False)
        self.assertEqual(1, len(errors))

        field, error = errors[0]
        self.assertEqual('lorem_ipsum_field', field)
        self.assertIsInstance(error, UnknownField)
        self.assertEqual('lorem_ipsum_field', error.message)
