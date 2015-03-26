from opengever.meeting.sablon import Sablon
from os.path import abspath
from os.path import dirname
from os.path import join
from unittest2 import TestCase
import json


class TestUnitSablon(TestCase):

    def test_sablon_availability(self):
        json_data = json.dumps({'foo': 42})

        template_path = join(dirname(abspath(__file__)),
                             'assets', 'sablon_template.docx')
        sablon = Sablon(template_path)
        sablon.process(json_data)

        self.assertEqual(0, sablon.returncode, msg=sablon.stderr)
