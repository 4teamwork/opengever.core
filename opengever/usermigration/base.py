from opengever.ogds.models.service import ogds_service
from opengever.usermigration.exceptions import UserMigrationException
from plone import api
import logging


logger = logging.getLogger('opengever.usermigration')


class BaseUserMigration(object):

    def __init__(self, portal, principal_mapping, mode='move'):
        if mode != 'move':
            raise NotImplementedError(
                u"Migration only supports 'move' mode"
            )

        self.portal = portal
        self.principal_mapping = principal_mapping
        self.mode = mode

    def _verify_user(self, userid):
        ogds_user = ogds_service().fetch_user(userid)
        if ogds_user is None:
            msg = u"User '{}' not found in OGDS!".format(userid)
            raise UserMigrationException(msg)


class BasePloneObjectAttributesMigrator(BaseUserMigration):

    fields_to_migrate = tuple()
    interface_to_query = None
    interface_to_adapt = None

    def __init__(self, portal, principal_mapping, mode='move'):
        super(BasePloneObjectAttributesMigrator, self).__init__(
            portal, principal_mapping, mode=mode
        )

        self.to_reindex = set()
        self.moves = {
            field_name: []
            for field_name in self.fields_to_migrate
        }

    def _verify_users(self):
        for new_userid in self.principal_mapping.values():
            self._verify_user(new_userid)

    @property
    def catalog_query(self):
        return {
            'object_provides': self.interface_to_query.__identifier__
        }

    def _iter_objects(self):
        catalog = api.portal.get_tool('portal_catalog')
        for brain in catalog.unrestrictedSearchResults(self.catalog_query):
            yield brain.getObject()

    def _migrate_object(self, obj):
        for field_name in self.fields_to_migrate:
            old_userid = getattr(obj, field_name, None)
            if old_userid in self.principal_mapping:
                path = '/'.join(obj.getPhysicalPath())
                logger.info('Fixing %r for %s' % (field_name, path))
                new_userid = self.principal_mapping[old_userid]
                setattr(obj, field_name, new_userid)
                self.to_reindex.add(obj)
                self.moves[field_name].append(
                    (path, old_userid, new_userid)
                )

    def _reindex_objects(self):
        for obj in self.to_reindex:
            logger.info('Reindexing %s' % '/'.join(obj.getPhysicalPath()))
            obj.reindexObject(idxs=self.fields_to_migrate)

    def _report_results(self):
        results = dict()
        for field_name, moves in self.moves.items():
            key = '.'.join([self.interface_to_adapt.__name__, field_name])
            results[key] = {
                'moved': moves,
                'copied': [],
                'deleted': [],
            }
        return results

    def migrate(self):
        self._verify_users()

        for obj in self._iter_objects():
            obj = self.interface_to_adapt(obj)
            self._migrate_object(obj)

        self._reindex_objects()
        return self._report_results()
