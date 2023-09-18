from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.model import create_session
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.map_local_roles import ROLEMAP_KEY
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import true
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


class MapPrincipalNamesToIDsSection(object):
    """Map local role principal names to IDs based on OGDS.

    Must be applied after the map-principals section.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        self.principal_ids_by_name = self.get_principal_mapping_from_ogds()

    def get_principal_mapping_from_ogds(self):
        session = create_session()

        principal_ids_by_name = {}

        # Groups take precedence over users
        columns_to_fetch = [
            (User.active, User.username, User.userid),
            (Group.active, Group.groupname, Group.groupid),
        ]

        for (active_col, name_col, id_col) in columns_to_fetch:
            query = (
                select((name_col, id_col))
                .where(active_col == true())
                .order_by(id_col)
            )

            # Make sure lookups by name are case-insensitive
            matches = [
                (row[name_col.name].lower(), row[id_col.name])
                for row in session.execute(query)
            ]
            principal_ids_by_name.update(dict(matches))

        return principal_ids_by_name

    def __iter__(self):
        for item in self.previous:
            if not self.principal_ids_by_name:
                yield item
                continue

            # What we operate on is a mapping of
            # <list of principal names> by <short role name>:
            # {
            #     'add': ['john.doe'],
            #     'edit': ['james.bond', 'administrators'],
            #     ...
            # }
            principals_by_role = item.get(ROLEMAP_KEY, {})

            for role_name, principal_names in principals_by_role.items():
                principal_ids = [
                    self.principal_ids_by_name.get(pn.lower(), pn)
                    for pn in principal_names
                ]
                principals_by_role[role_name] = principal_ids

            yield item
