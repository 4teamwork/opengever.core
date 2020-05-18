from opengever.core.upgrade import SQLUpgradeStep
from plone import api
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import table
import logging


LOG = logging.getLogger('ftw.upgrade')

favorites_table = table(
    'favorites',
    column('id'),
    column('plone_uid'),
    column('admin_unit_id'),
    column('filename'),
)


class PopulateFilenameColumnInFavorites(SQLUpgradeStep):
    """Populate filename column in favorites.
    """

    def migrate(self):
        current_admin_unit_id = api.portal.get_registry_record(
            'opengever.ogds.base.interfaces.IAdminUnitConfiguration.current_unit_id'
        )
        rows = self.execute(
            select([favorites_table.c.plone_uid])
            .where(favorites_table.c.admin_unit_id == current_admin_unit_id)
            .distinct()
        ).fetchall()
        favorite_uids = [row[0] for row in rows]

        query = {"object_provides": "opengever.document.behaviors.IBaseDocument",
                 "UID": favorite_uids}
        for brain in self.catalog_unrestricted_search(query=query):
            filename = brain.filename or u""
            self.execute(
                favorites_table.update()
                .values(filename=filename)
                .where(favorites_table.c.plone_uid == brain.UID)
                .where(favorites_table.c.admin_unit_id == current_admin_unit_id))
