from datetime import datetime
from opengever.meeting.interfaces import IMeetingSettings
from opengever.meeting.utils import format_date
from opengever.meeting.utils import JsonDataProcessor
from opengever.testing import FunctionalTestCase
from plone import api


class TestJsonDataProcessor(FunctionalTestCase):

    def test_format_date_function(self):
        date = datetime(2016, 12, 3)
        self.assertEqual("03.12.2016", format_date(date))

        api.portal.set_registry_record("sablon_date_format_string", u'%A %d %B', IMeetingSettings)
        self.assertEqual("Saturday 03 December", format_date(date))

    def test_processor_finds_fields(self):
        processor = JsonDataProcessor()
        data = {"key1": "field1",
                "key2": {"key3": "field3",
                         "key4": {"key5": "field5"}}}

        expected_processed_data = {"key1": "Field1",
                                   "key2": {"key3": "field3",
                                            "key4": {"key5": "Field5"}}}
        field_list = (("key1",), ("key2", "key4", "key5"))
        capitalize = lambda field: field.capitalize()
        transform_list = (capitalize, capitalize)

        self.assertEqual(processor.process(data, field_list, transform_list),
                         expected_processed_data)

    def test_processor_date_processing(self):
        processor = JsonDataProcessor()
        data = {"key1": "field1",
                "key2": {"key3": datetime(2016, 12, 3),
                         "key4": {"key5": "field5"}}}

        capitalize = lambda field: field.capitalize()
        field_list = (("key1",), ("key2", "key3"))
        transform_list = (capitalize, format_date)
        expected_processed_data = {"key1": "Field1",
                                   "key2": {"key3": "03.12.2016",
                                            "key4": {"key5": "field5"}}}
        self.assertEqual(processor.process(data, field_list, transform_list),
                         expected_processed_data)
