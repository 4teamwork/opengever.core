from opengever.base.model import is_oracle
from opengever.core.upgrade import SchemaMigration
from opengever.globalindex.model.task import TaskPrincipal
from sqlalchemy import func
from sqlalchemy import Index


INDEX_NAME = 'task_principals_ix'


class AddIndexForTaskPrincipal(SchemaMigration):
    """Add Index for task principal.
    """

    def migrate(self):
        if is_oracle() and not self._has_index(INDEX_NAME, 'task_principals'):
            task_principals_ix = Index(
                INDEX_NAME,
                func.nlssort(TaskPrincipal.principal, 'NLS_SORT=GERMAN_CI'))

            task_principals_ix.create(self.session.bind)
