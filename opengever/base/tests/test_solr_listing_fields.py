from opengever.base.solr.fields import SimpleListingField
from unittest import TestCase


class MyCustomField(SimpleListingField):

    def index_value_to_label(self, value):
        colors = {'red': 'RED'}
        return colors[value]


class TestSolrListingFields(TestCase):

    def test_safe_index_value_to_label(self):
        field = MyCustomField('color')

        with self.assertRaises(KeyError):
            field.index_value_to_label('doesnt-exist')

        self.assertEqual('RED', field.safe_index_value_to_label('red'))
        self.assertEqual('doesnt-exist', field.safe_index_value_to_label('doesnt-exist'))
