from Acquisition import aq_base
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
    column('review_state'),
    column('is_subdossier'),
    column('is_leafnode'),
)


class PopulateAdditionalMetadataOfFavorites(SQLUpgradeStep):
    """Populate additional metadata of favorites.
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
            obj = self.catalog_unrestricted_get_object(brain)

            review_state = brain.review_state
            # avoid storing empty string or Missing.Value
            if not review_state:
                review_state = None

            is_subdossier = None
            if hasattr(aq_base(obj), 'is_subdossier'):
                is_subdossier = obj.is_subdossier()

            is_leafnode = None
            if brain.portal_type == 'opengever.repository.repositoryfolder':
                is_leafnode = not brain.has_sametype_children

            self.execute(
                favorites_table.update()
                .values(review_state=review_state, is_subdossier=is_subdossier, is_leafnode=is_leafnode)
                .where(favorites_table.c.plone_uid == plone_uid)
                .where(favorites_table.c.admin_unit_id == current_admin_unit_id)
            )
