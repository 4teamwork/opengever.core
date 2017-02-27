from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.repository.interfaces import IRepositoryFolderRecords
from plone import api
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger('opengever.bundle.late_validation')
log.setLevel(logging.INFO)


def get_nesting_levels_config():
    """Returns the configuration of max nesting levels for repofolders and
    dossiers as a {portal_type: max_level} dictionary.
    """
    max_repofolder_depth = api.portal.get_registry_record(
        'maximum_repository_depth', interface=IRepositoryFolderRecords)

    # This is actually the maximum levels of *sub*dossiers allowed. That's
    # why we increase this value by one below, in order to get the maximum
    # allowed nesting level for dossiers in general.
    max_subdossier_depth = api.portal.get_registry_record(
        'maximum_dossier_depth', interface=IDossierContainerTypes)

    config = {
        'opengever.repository.repositoryfolder': max_repofolder_depth,
        'opengever.dossier.businesscasedossier': max_subdossier_depth + 1,
    }
    return config


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
        self.nesting_levels_config = get_nesting_levels_config()

    def __iter__(self):
        for item in self.previous:
            self.validate_nesting_depth(item)
            yield item

    def validate_nesting_depth(self, item):
        if item['_type'] not in self.nesting_levels_config:
            return

        level = item['_nesting_depth']
        max_level = self.nesting_levels_config[item['_type']]

        if level > max_level:
            warning = (item['guid'], max_level, level, item['_path'])
            self.bundle.warnings['max_nesting_depth_exceeded'].append(warning)
            log.warn('Max nesting depth exceeded (max=%s, actual=%s): %s' % (
                     max_level, level, item['_path']))
