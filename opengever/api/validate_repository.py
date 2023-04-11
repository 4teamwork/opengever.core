from base64 import b64decode
from jsonschema import ValidationError
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.bundle.factory import BundleFactory
from opengever.bundle.factory import parse_args
from opengever.bundle.loader import BundleLoader
from opengever.bundle.xlsx import InvalidXLSXException
from path import Path
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from tempfile import mkdtemp
from tempfile import NamedTemporaryFile
import os


class TemporaryDirectory(object):

    def __enter__(self):
        self._tempdir_path = Path(mkdtemp(prefix='opengever.core.repository_validator_'))
        return self._tempdir_path

    def __exit__(self, exc_type, exc_value, tb):
        self._tempdir_path.rmtree_p()


class ValidateRepository(Service):
    """Endpoint to validate a repository excel file"""

    def reply(self):
        data = json_body(self.request)
        file_ = data.get('file')
        if not file_:
            raise NotReportedBadRequest('Missing file.')

        try:
            with TemporaryDirectory() as tmpdirname:
                with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
                    tmpfile.write(b64decode(file_.get("data")))
                    tmpfile.flush()

                    args = parse_args([tmpfile.name,
                                       tmpdirname,
                                      '--users-group', 'Test group'])
                    factory = BundleFactory(args)
                    factory.dump_bundle()

                loader = BundleLoader(os.path.join(factory.target_dir, factory.bundle_name))
                loader.load()

        except (ValidationError, InvalidXLSXException) as exc:
            raise NotReportedBadRequest(exc.message)
