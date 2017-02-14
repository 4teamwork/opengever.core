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
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import os.path


logger = logging.getLogger('opengever.setup.sections.fileloader')


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

        self.bundle.errors['files_not_found'] = {}
        self.bundle.errors['files_io_errors'] = {}
        self.bundle.errors['msgs'] = {}

    def is_mail(self, item):
        return item['_type'] == 'ftw.mail.mail'

    def __iter__(self):
        for item in self.previous:

            if self.is_mail(item):
                file_field = IMail['message']
            else:
                file_field = IDocumentSchema['file']

            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]

            if self.key in item:
                filepath = item[self.key]
                if filepath is None:
                    yield item
                    continue

                if pathkey not in item:
                    logger.warning("Missing path key for file %s" % filepath)
                    yield item
                    continue
                path = item[pathkey]

                filepath = os.path.join(self.bundle_path, filepath)
                filename = os.path.basename(filepath)

                # TODO: Check for this in OGGBundle validation
                if filepath.endswith(u'.msg'):
                    logger.warning("Skipping .msg file: %s" % filepath)
                    self.bundle.errors['msgs'][filepath] = path
                    yield item
                    continue

                # TODO: Check for this in OGGBundle validation
                if not os.path.exists(filepath):
                    logger.warning("File not found: %s" % filepath)
                    self.bundle.errors['files_not_found'][filepath] = path
                    yield item
                    continue

                mimetype, _encoding = guess_type(filepath, strict=False)
                if mimetype is None:
                    logger.warning("Unknown mimetype for file %s" % filepath)
                    mimetype = 'application/octet-stream'

                obj = item.get('_object')
                if obj is None:
                    logger.warning(
                        "Cannot set file. Document %s doesn't exist." % path)
                    yield item
                    continue

                try:
                    with open(filepath, 'rb') as f:
                        namedblobfile = file_field._type(
                            data=f.read(),
                            contentType=mimetype,
                            filename=filename)
                        setattr(obj, file_field.getName(), namedblobfile)
                except EnvironmentError as e:
                    # TODO: Check for this in OGGBundle validation
                    logger.warning("Can't open file %s. %s." % (
                        filepath, str(e)))
                    self.bundle.errors['files_io_errors'][filepath] = path
                    yield item
                    continue

                # Fire these event handlers manually because they got fired
                # too early before (when the file contents weren't loaded yet)
                if self.is_mail(item):
                    initialize_metadata(obj, None)
                    # Reset the [No Subject] placeholder
                    obj.title = None
                    initalize_title(obj, None)
                else:
                    sync_title_and_filename_handler(obj, None)
                    set_digitally_available(obj, None)

            yield item
