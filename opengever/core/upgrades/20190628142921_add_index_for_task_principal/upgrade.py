from opengever.base.model import is_oracle
from opengever.core.upgrade import SchemaMigration
from opengever.globalindex.model.task import TaskPrincipal
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddIndexForTaskPrincipal(SchemaMigration):
    """Add Index for task principal.
    """

    principal_table = table(
        "task_principals",
        column("task_id"),
        column("principal")
    )

    def migrate(self):
        if is_oracle():
            task_principals_ix = Index(
                'task_principals_ix',
                func.nlssort(TaskPrincipal.principal, 'NLS_SORT=GERMAN_CI'))

            task_principals_ix.create(self.session.bind)
