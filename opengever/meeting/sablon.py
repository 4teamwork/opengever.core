from opengever.meeting.exceptions import SablonProcessingFailed
from os import environ
from os.path import join
from subprocess32 import PIPE
from subprocess32 import Popen
import shutil
import tempfile


class Sablon(object):
    """Integrate word document template processor.

    See https://github.com/senny/sablon

    """
    def __init__(self, template):
        self.template = template
        self.returncode = None
        self.stdout = None
        self.stderr = None
        self.file_data = None

    def process(self, json_data, namedblobfile=None):

        tmpdir_path = tempfile.mkdtemp(prefix='opengever.core.sablon_')
        output_path = join(tmpdir_path, 'sablon_output.docx')

        if namedblobfile is None:
            template_path = self.template.as_file(tmpdir_path)
        else:
            template_path = join(tmpdir_path, namedblobfile.filename)
            with open(template_path, 'wb') as template_file:
                template_file.write(namedblobfile.data)

        try:
            sablon_path = environ.get('SABLON_BIN', 'sablon')
            subprocess = Popen(
                [sablon_path, template_path, output_path],
                stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self.stdout, self.stderr = subprocess.communicate(input=json_data)
            self.returncode = subprocess.returncode
            if not self.is_processed_successfully():
                raise SablonProcessingFailed(self.stderr)
            with open(output_path, 'rb') as outfile:
                self.file_data = outfile.read()
        finally:
            shutil.rmtree(tmpdir_path)

        return self

    def is_processed_successfully(self):
        return self.returncode == 0
