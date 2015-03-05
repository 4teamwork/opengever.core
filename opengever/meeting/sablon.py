from os.path import join
from subprocess32 import PIPE
from subprocess32 import Popen
import shutil
import tempfile


class Sablon(object):
    """Integrate word document template processor.

    See https://github.com/senny/sablon

    """
    def __init__(self, template_path):
        self.template_path = template_path
        self.returncode = None
        self.stdout = None
        self.stderr = None
        self.file_data = None

    def process(self, json_data):
        tmpdir_path = tempfile.mkdtemp(prefix='opengever.core.sablon_')
        output_path = join(tmpdir_path, 'sablon_output.docx')

        try:
            sablon_path = environ.get('SABLON_BIN', 'sablon')
            subprocess = Popen(
                [sablon_path, self.template_path, output_path],
                stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self.stdout, self.stderr = subprocess.communicate(input=json_data)
            self.returncode = subprocess.returncode
            if self.is_processed_successfully():
                with open(output_path, 'rb') as outfile:
                    self.file_data = outfile.read()
        finally:
            shutil.rmtree(tmpdir_path)

    def is_processed_successfully(self):
        return self.returncode == 0
