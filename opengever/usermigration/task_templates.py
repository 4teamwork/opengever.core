from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.usermigration.base import BasePloneObjectAttributesMigrator


class TaskTemplateMigrator(BasePloneObjectAttributesMigrator):
    """Migrate the `issuer` and `responsible` fields on task templates."""

    fields_to_migrate = ('responsible', 'issuer')
    interface_to_query = ITaskTemplate
    interface_to_adapt = ITaskTemplate
