from os.path import abspath
from os.path import dirname
from os.path import join
from subprocess32 import PIPE
from subprocess32 import Popen
from unittest2 import TestCase
import json
import shutil
import tempfile


class TestUnitSablon(TestCase):

    def test_sablon_availability(self):
        json_data = json.dumps({'foo': 42})

        template_path = join(dirname(abspath(__file__)),
                             'assets', 'sablon_template.docx')
        tmpdir_path = tempfile.mkdtemp(prefix='opengever.core.sablon._tests_')
        output_path = join(tmpdir_path, 'sablon_output.docx')
        try:
            process = Popen(
                ['sablon', template_path, output_path],
                universal_newlines=True,
                stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate(input=json_data)
            self.assertEqual(0, process.returncode, msg=stderr)
        finally:
            shutil.rmtree(tmpdir_path)
