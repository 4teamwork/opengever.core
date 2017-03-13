from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


AC_LOCAL_ROLES_KEY = '_ac_local_roles'


class MapPrincipalsSection(object):
    """Map local role principal names based on a mapping given in
    ingestion settings.

    Must be applied after the map-local-roles section.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]

    def __iter__(self):
        ingestion_settings = self.bundle.ingestion_settings
        principal_mapping = ingestion_settings.get('principal_mapping', {})

        for item in self.previous:
            if not principal_mapping:
                yield item
                continue

            local_roles = item.get(AC_LOCAL_ROLES_KEY)
            if local_roles:
                for old_principal, new_principal in principal_mapping.items():
                    if old_principal in local_roles:
                        # We wouldn't want to overwrite existing entries
                        assert new_principal not in local_roles
                        local_roles[new_principal] = local_roles[old_principal]
                        local_roles.pop(old_principal)

            yield item
