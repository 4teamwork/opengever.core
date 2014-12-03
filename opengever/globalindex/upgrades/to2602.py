from ftw.upgrade import UpgradeStep
from opengever.core.model import create_session
from opengever.ogds.models.utils import alter_column_length


class IncreaseTaskPrincipalColumnLength(UpgradeStep):
    """Increase Task `principal` column length in GlobalIndex SQL schema."""

    def __call__(self):
        session = create_session()
        alter_column_length(session, 'task_principals', 'principal', 255)
