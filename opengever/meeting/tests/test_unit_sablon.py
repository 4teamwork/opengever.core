from opengever.core.docker_testing import SABLON_SERVICE_FIXTURE
from opengever.meeting.sablon import Sablon
from opengever.testing import assets
from pkg_resources import resource_filename
from StringIO import StringIO
from unittest import TestCase
import json


class MockFile(object):
    def open(self):
        return StringIO(assets.load('sablon_template.docx'))


class MockTemplate(object):
    """Return hardcoded path to test asset template."""

    def as_file(self, path):
        template_path = resource_filename('opengever.testing.assets',
                                          'sablon_template.docx')
        return template_path

    @property
    def file(self):
        return MockFile()


class TestUnitSablon(TestCase):

    def test_sablon_availability(self):
        json_data = json.dumps({'foo': 42})

        sablon = Sablon(MockTemplate())
        sablon.process(json_data)

        self.assertEqual(0, sablon.returncode, msg=sablon.stderr)


class TestSablonService(TestCase):

    layer = SABLON_SERVICE_FIXTURE

    def test_sablon_produces_docx_using_service(self):
        json_data = json.dumps({'foo': 42})
        sablon = Sablon(MockTemplate())
        sablon.process(json_data)
        # We just check if we got a ZIP archive which is what a .docx actually is
        self.assertTrue(
            sablon.file_data.startswith('PK\x03\x04'),
            'Does not look like a DOCX archive',
        )
