from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from ftw.mail.mail import IMail
from mimetypes import guess_type
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.document.document import IDocumentSchema
from opengever.document.subscribers import set_digitally_available
from opengever.document.subscribers import sync_title_and_filename_handler
from opengever.mail.mail import initalize_title
from opengever.mail.mail import initialize_metadata
from opengever.mail.mail import NO_SUBJECT_TITLE_FALLBACK
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import ntpath
import os.path
import posixpath


logger = logging.getLogger('opengever.setup.sections.fileloader')


INVALID_FILE_EXTENSIONS = ('.msg', '.exe', '.dll')


class FileLoadingFailed(Exception):
    """A file could not be loaded.
    """


class FileLoaderSection(object):
    """Stores file data directly in already constructed content items."""

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        # TODO: Might want to also use defaultMatcher for this key to make it
        # configurable instead of hard coding it here.
        self.key = 'filepath'
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')

        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        self.bundle_path = IAnnotations(transmogrifier)[BUNDLE_PATH_KEY]

        self.bundle.errors['files_not_found'] = []
        self.bundle.errors['files_io_errors'] = []
        self.bundle.errors['files_unresolvable_path'] = []
        self.bundle.errors['files_invalid_types'] = []
        self.bundle.errors['unmapped_unc_mounts'] = set()

    def __iter__(self):
        for item in self.previous:
            guid = item['guid']
            file_field = self.get_file_field(item)

            try:
                abs_filepath, path = self.get_abs_filepath(item)
                self.validate_filepath(item, abs_filepath, path)
            except FileLoadingFailed:
                yield item
                continue

            obj = item.get('_object')
            if obj is None:
                logger.warning(
                    "Cannot set file. Document %s doesn't exist." % path)
                yield item
                continue

            try:
                self.add_namedblob_file(abs_filepath, file_field, obj)
            except EnvironmentError as e:
                # TODO: Check for this in OGGBundle validation
                logger.warning(
                    "Can't open file %s. %s." % (abs_filepath, str(e)))
                error = (guid, abs_filepath, str(e), path)
                self.bundle.errors['files_io_errors'].append(error)

            self.run_after_creation_jobs(item, obj)

            yield item

    def is_mail(self, item):
        return item['_type'] == 'ftw.mail.mail'

    def _is_absolute_path(self, path):
        if posixpath.isabs(path):
            return True

        if ntpath.isabs(path):
            return True

        return False

    def _is_unc_path(self, filepath):
        return filepath.startswith('\\\\')

    def _translate_unc_path(self, filepath):
        ingestion_settings = self.bundle.ingestion_settings
        unc_mount_mapping = ingestion_settings.get('unc_mounts', {})
        mount, rest = ntpath.splitunc(filepath)

        if mount not in unc_mount_mapping:
            logger.warning('UNC mount %s is not mapped!' % mount)
            self.bundle.errors['unmapped_unc_mounts'].add((mount, ))
            return None

        # posix_mountpoint is the location where the fileshare has been
        # mounted on the POSIX system (Linux / OS X)
        posix_mountpoint = unc_mount_mapping[mount]
        relative_path = rest.replace('\\', '/').lstrip('/')
        abs_filepath = os.path.join(posix_mountpoint, relative_path)
        return abs_filepath

    def build_absolute_filepath(self, filepath):
        if not self._is_absolute_path(filepath):
            filepath = os.path.join(self.bundle_path, filepath)

        if self._is_unc_path(filepath):
            filepath = self._translate_unc_path(filepath)

        return filepath

    def get_file_field(self, item):
        if self.is_mail(item):
            return IMail['message']
        return IDocumentSchema['file']

    def add_namedblob_file(self, abs_filepath, field, obj):
        mimetype, _encoding = guess_type(abs_filepath, strict=False)
        if mimetype is None:
            logger.warning(
                "Unknown mimetype for file %s" % abs_filepath)
            mimetype = 'application/octet-stream'

        with open(abs_filepath, 'rb') as f:
            namedblobfile = field._type(
                data=f.read(),
                contentType=mimetype,
                filename=self.get_filename(abs_filepath))
            setattr(obj, field.getName(), namedblobfile)

    def run_after_creation_jobs(self, item, obj):
        """Fire these event handlers manually because they got fired
        too early before (when the file contents weren't loaded yet)
        """
        if self.is_mail(item):
            initialize_metadata(obj, None)
            if obj.title == NO_SUBJECT_TITLE_FALLBACK:
                # Reset the [No Subject] placeholder
                obj.title = None
                initalize_title(obj, None)
        else:
            sync_title_and_filename_handler(obj, None)
            set_digitally_available(obj, None)

    def get_abs_filepath(self, item):
        _filepath = item.get(self.key)
        if not _filepath:
            raise FileLoadingFailed()

        pathkey = self.pathkey(*item.keys())[0]
        path = item.get(pathkey)
        if not path:
            logger.warning("Missing path key for file %s" % _filepath)
            raise FileLoadingFailed()

        abs_filepath = self.build_absolute_filepath(_filepath)
        if abs_filepath is None:
            logger.warning('Unresolvable filepath: %s' % _filepath)
            error = (item['guid'], _filepath, path)
            self.bundle.errors['files_unresolvable_path'].append(error)
            raise FileLoadingFailed

        return abs_filepath, path

    def validate_filepath(self, item, abs_filepath, path):
        # TODO: Move does checks to OGGBundle validation
        if any(abs_filepath.lower().endswith(ext) for ext in INVALID_FILE_EXTENSIONS):  # noqa
            logger.warning(
                "Skipping file with invalid type: %s" % abs_filepath)
            error = (item['guid'], abs_filepath, path)
            self.bundle.errors['files_invalid_types'].append(error)
            raise FileLoadingFailed()

        if not os.path.exists(abs_filepath):
            logger.warning("File not found: %s" % abs_filepath)
            error = (item['guid'], abs_filepath, path)
            self.bundle.errors['files_not_found'].append(error)
            raise FileLoadingFailed()

    def get_filename(self, abs_filepath):
        filename = os.path.basename(abs_filepath)
        if isinstance(filename, str):
            filename = filename.decode('utf8')

        return filename
