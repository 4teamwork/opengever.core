from opengever.base.model import is_oracle
from opengever.core.upgrade import SchemaMigration
from opengever.globalindex.model.task import TaskPrincipal
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy.sql.expression import text


INDEX_NAME = 'task_principals_ix'


class AddIndexForTaskPrincipal(SchemaMigration):
    """Add Index for task principal.
    """

    def _has_index(self, idxname):
        stmt = text("SELECT COUNT(*) FROM user_indexes WHERE index_name = :idxname")
        stmt = stmt.bindparams(idxname=idxname)
        count = self.session.execute(stmt).scalar()
        return count > 0

    def migrate(self):
        if is_oracle():
            if self._has_index(INDEX_NAME):
                return

            task_principals_ix = Index(
                INDEX_NAME,
                func.nlssort(TaskPrincipal.principal, 'NLS_SORT=GERMAN_CI'))

            task_principals_ix.create(self.session.bind)
