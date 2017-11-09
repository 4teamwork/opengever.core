from opengever.base.oguid import Oguid
from opengever.core.upgrade import SQLUpgradeStep
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


meetings_table = table(
    "meetings",
    column("id"),
    column("title"),
    column("dossier_admin_unit_id"),
    column("dossier_int_id"),
)


class SyncMeetingTitleToDossier(SQLUpgradeStep):
    """Sync meeting title to dossier.
    """

    def migrate(self):
        for meeting in self.execute(meetings_table.select()).fetchall():
            self.sync_title_to_meeting_dossier(meeting)

    def sync_title_to_meeting_dossier(self, meeting):
        dossier_oguid = Oguid(
            meeting.dossier_admin_unit_id, meeting.dossier_int_id)
        dossier = dossier_oguid.resolve_object()

        if not dossier:
            return

        dossier.title = meeting.title
        dossier.reindexObject(idxs=['Title', 'SearchableText'])
