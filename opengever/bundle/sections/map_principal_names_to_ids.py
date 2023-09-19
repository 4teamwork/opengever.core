from collections import defaultdict
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


CHECK_UNIQUE_PRINCIPALS_KEY = 'check_unique_principals'


class AmbiguousPrincipalNames(Exception):
    pass


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
        self.check_unique_principals = IAnnotations(transmogrifier).get(
            CHECK_UNIQUE_PRINCIPALS_KEY, True)
        self.principal_ids_by_name = self.get_principal_mapping_from_ogds()

    def get_principal_mapping_from_ogds(self):
        session = create_session()

        principal_ids_by_name = {}
        ambig_names_by_type = {}

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

            matches = [
                (row[name_col.name], row[id_col.name])
                for row in session.execute(query)
            ]

            ids_by_name = dict(matches)

            # Check that principal names are unambiguous in regard to casing
            if self.check_unique_principals:
                principal_type = name_col.name
                ambig_names_by_type[principal_type] = self.find_non_unique(ids_by_name)

            # Make sure lookups by name are case-insensitive
            for name, id_ in ids_by_name.items():
                principal_ids_by_name[name.lower()] = id_

        if self.check_unique_principals and any(ambig_names_by_type.values()):
            self.report_non_unique(ambig_names_by_type)
            raise AmbiguousPrincipalNames(
                'Ambiguous principal names in OGDS found. See above.')

        return principal_ids_by_name

    def find_non_unique(self, ids_by_name):
        """Find OGDS user / group names that are ambiguous regarding case.
        """
        ambig_names = defaultdict(list)

        for name, id_ in ids_by_name.items():
            ambig_names[name.lower()].append((name, id_))

        for lower_name, matching_names in ambig_names.items():
            if len(matching_names) == 1:
                ambig_names.pop(lower_name)

        return ambig_names

    def report_non_unique(self, ambig_names_by_type):
        log = self.logger.error
        log('Found ambiguous principal names in OGDS.')
        log('The following users/groups are not case-insensitively unique:')
        log('')

        for principal_type, dupes_by_lower in ambig_names_by_type.items():
            for lower_name, duplicates in dupes_by_lower.items():
                log(
                    '%s "%s" matches multiple records:' % (principal_type, lower_name))

                for name, id_ in duplicates:
                    log('  %s: %s (id: %s)' % (principal_type, name, id_))

                log('')
        log('Skip this check by running import with '
            '--no-check-unique-principals flag')

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
