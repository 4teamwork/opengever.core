from opengever.base.model import create_session
from opengever.core.upgrade import SchemaMigration
from opengever.ogds.models import BASE
from opengever.ogds.models import get_tables


class AddLocksTable(SchemaMigration):

    profileid = 'opengever.ogds.base'
    upgradeid = 4500

    def migrate(self):
        BASE.metadata.create_all(
            create_session().bind,
            tables=get_tables(['locks']),
            checkfirst=True)
