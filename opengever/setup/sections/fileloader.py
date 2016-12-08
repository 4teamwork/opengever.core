from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import traverse
from mimetypes import guess_type
from opengever.document.document import IDocumentSchema
from opengever.document.subscribers import set_digitally_available
from opengever.document.subscribers import sync_title_and_filename_handler
from opengever.setup.sections.jsonsource import BUNDLE_PATH_KEY
from opengever.setup.sections.jsonsource import JSON_STATS_KEY
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

        self.bundle_path = IAnnotations(transmogrifier)[BUNDLE_PATH_KEY]

        # TODO: Handle .eml / ftw.mail.mail
        self.file_field_class = IDocumentSchema['file']._type

        self.stats = IAnnotations(transmogrifier)[JSON_STATS_KEY]
        self.stats['errors']['files_not_found'] = {}
        self.stats['errors']['files_io_errors'] = {}
        self.stats['errors']['msgs'] = {}

    def __iter__(self):
        for item in self.previous:
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
                    self.stats['errors']['msgs'][filepath] = path
                    yield item
                    continue

                # TODO: Check for this in OGGBundle validation
                if not os.path.exists(filepath):
                    logger.warning("File not found: %s" % filepath)
                    self.stats['errors']['files_not_found'][filepath] = path
                    yield item
                    continue

                mimetype, _encoding = guess_type(filepath, strict=False)
                if mimetype is None:
                    logger.warning("Unknown mimetype for file %s" % filepath)
                    mimetype = 'application/octet-stream'

                obj = traverse(self.context, path, None)
                if obj is None:
                    logger.warning(
                        "Cannot set file. Document %s doesn't exist." % path)
                    yield item
                    continue

                try:
                    with open(filepath, 'rb') as f:
                        obj.file = self.file_field_class(
                            data=f.read(),
                            contentType=mimetype,
                            filename=filename)
                except EnvironmentError as e:
                    # TODO: Check for this in OGGBundle validation
                    logger.warning("Can't open file %s. %s." % (
                        filepath, str(e)))
                    self.stats['errors']['files_io_errors'][filepath] = path
                    yield item
                    continue

                sync_title_and_filename_handler(obj, None)
                set_digitally_available(obj, None)

            yield item
