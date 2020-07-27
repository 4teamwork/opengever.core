from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.schemadump.config import ROLES_BY_SHORTNAME
from zope.interface import classProvides
from zope.interface import implements
import logging


BLOCK_INHERITANCE_KEY = 'block_inheritance'
ROLEMAP_KEY = '_permissions'

# See opengever.base.schemadump.config for short role name definitions


class MapLocalRolesSection(object):
    """Map local roles from short names used in OGGBundles to actual role names
    and prepare them in a way so that collective.blueprint.jsonmigrator can
    deal with them.

    For example, this section transforms a rolemap from an OGGBundle looking
    like this

    '_permissions': {
      'block_inheritance': True,
      'read': ['regular_users', 'admin_users'],
      'reactivate': ['admin_users']
    }

    to this:

    'block_inheritance': True,
    '_ac_local_roles': {'regular_users': ['Reader'],
                        'admin_users': ['Reader', 'Publisher']},
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])

    def __iter__(self):
        for item in self.previous:
            rolemap = item.get(ROLEMAP_KEY)
            if rolemap:
                # Move block_inheritance flag to top-level (if present)
                block = rolemap.get(BLOCK_INHERITANCE_KEY)
                if block is not None:
                    item[BLOCK_INHERITANCE_KEY] = block

                # Map short names to actual role names, and invert the mapping
                # from {role: principals} to {principal: roles}
                roles_by_principal = {}
                for role_shortname, role in ROLES_BY_SHORTNAME.items():
                    principals = rolemap.get(role_shortname, [])
                    for principal in principals:
                        if principal not in roles_by_principal:
                            roles_by_principal[principal] = []
                        roles_by_principal[principal].append(role)

                item['_ac_local_roles'] = roles_by_principal
                item.pop(ROLEMAP_KEY)

            yield item
