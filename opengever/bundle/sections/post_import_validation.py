from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger('opengever.bundle.late_validation')
log.setLevel(logging.INFO)


# XXX: Read this from actual bundle configuration
MAX_NESTING_LEVELS = {
    'opengever.repository.repositoryfolder': 3,
    'opengever.dossier.businesscasedossier': 2,
}


class PostImportValidationSection(object):
    """Perform some additional validations after import.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        self.bundle.warnings['max_nesting_depth_exceeded'] = []

    def __iter__(self):
        for item in self.previous:
            self.validate_nesting_depth(item)
            yield item

    def validate_nesting_depth(self, item):
        if item['_type'] not in MAX_NESTING_LEVELS:
            return

        level = item['_nesting_depth']
        max_level = MAX_NESTING_LEVELS[item['_type']]

        if level > max_level:
            warning = (item['guid'], max_level, level, item['_path'])
            self.bundle.warnings['max_nesting_depth_exceeded'].append(warning)
            log.warn('Max nesting depth exceeded (max=%s, actual=%s): %s' % (
                     max_level, level, item['_path']))
