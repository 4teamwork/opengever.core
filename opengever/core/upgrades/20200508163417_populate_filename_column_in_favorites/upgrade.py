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
        plone_uids = [row[0] for row in rows]

        for plone_uid in plone_uids:
            brains = self.catalog_unrestricted_search({'UID': plone_uid})
            if len(brains) != 1:
                LOG.error(
                    'Could not find a unique brain for the UID={}'.format(plone_uid)
                )
                continue
            brain = brains[0]

            filename = brain.filename
            self.execute(
                favorites_table.update()
                .values(filename=filename)
                .where(favorites_table.c.plone_uid == plone_uid)
                .where(favorites_table.c.admin_unit_id == current_admin_unit_id)
            )
