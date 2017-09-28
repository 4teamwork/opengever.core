from opengever.meeting.sablon import Sablon
from pkg_resources import resource_filename
from unittest import TestCase
import json


class MockTemplate(object):
    """Return hardcoded path to test asset template."""

    def as_file(self, path):
        template_path = resource_filename('opengever.testing.assets',
                                          'sablon_template.docx')
        return template_path


class TestUnitSablon(TestCase):

    def test_sablon_availability(self):
        json_data = json.dumps({'foo': 42})

        sablon = Sablon(MockTemplate())
        sablon.process(json_data)

        self.assertEqual(0, sablon.returncode, msg=sablon.stderr)
