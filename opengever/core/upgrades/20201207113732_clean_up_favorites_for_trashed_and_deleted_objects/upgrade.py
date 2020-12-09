from opengever.core.upgrade import SQLUpgradeStep
from plone import api
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import table
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import logging


LOG = logging.getLogger('ftw.upgrade')

favorites_table = table(
    'favorites',
    column('id'),
    column('plone_uid'),
    column('admin_unit_id'),
    column('int_id'),
)


class CleanUpFavoritesForTrashedAndDeletedObjects(SQLUpgradeStep):
    """Clean up favorites for trashed and deleted objects.
    """

    deferrable = True

    def migrate(self):

        # We delete all favorites for trashed objects
        current_admin_unit_id = api.portal.get_registry_record(
            'opengever.ogds.base.interfaces.IAdminUnitConfiguration.current_unit_id'
        )
        rows = self.execute(
            select([favorites_table.c.plone_uid])
            .where(favorites_table.c.admin_unit_id == current_admin_unit_id)
            .distinct()
        ).fetchall()
        favorite_uids = [row[0] for row in rows]

        query = {"trashed": True,
                 "UID": favorite_uids}
        trashed_uids = [brain.UID for brain in
                        self.catalog_unrestricted_search(query=query)]
        self.execute(
            favorites_table.delete()
            .where(favorites_table.c.plone_uid.in_(trashed_uids))
            .where(favorites_table.c.admin_unit_id == current_admin_unit_id))

        # Now we delete all favorites for objects that have been deleted, i.e.
        # that are not in the catalog
        intids = getUtility(IIntIds)

        rows = self.execute(
            select([favorites_table.c.int_id])
            .where(favorites_table.c.admin_unit_id == current_admin_unit_id)
            .distinct()
        ).fetchall()

        favorites_to_delete = [row[0] for row in rows if row[0] not in intids]
        self.execute(
            favorites_table.delete()
            .where(favorites_table.c.int_id.in_(favorites_to_delete))
            .where(favorites_table.c.admin_unit_id == current_admin_unit_id))
