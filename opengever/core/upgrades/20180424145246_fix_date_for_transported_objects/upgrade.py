from datetime import datetime
from opengever.core.upgrade import SQLUpgradeStep
from opengever.document.behaviors import IBaseDocument
from opengever.task.task import ITask


TASK_DATE_FIELDS = [
    ('deadline', 'deadline'),
    ('date_of_completion', 'date_of_completion'),
    ('expectedStartOfWork', None)]

DOCUMENT_DATE_FIELDS = [
    ('document_date', 'document_date'),
    ('receipt_date', 'receipt_date'),
    ('delivery_date', 'delivery_date')]


class FixDateForTransportedObjects(SQLUpgradeStep):
    """Fix date for transported objects.
    """

    # This upgrade step was retroactively marked as deferrable.
    # There is no need to fix the dates immediately, there have been broken
    # for quit a long time.
    deferrable = True

    def migrate(self):
        if not self.has_multiple_admin_units():
            # Transporter is only used on deployments with multiple adminunits,
            # therefore we skip on single admin unit sites.
            return

        query = {'object_provides': ITask.__identifier__}
        for obj in self.objects(query, 'Fix task dates'):
            self.fix_task_dates(obj)

        query = {'object_provides': IBaseDocument.__identifier__}
        for obj in self.objects(query, 'Fix document dates'):
            self.fix_document_dates(obj)

    def fix_task_dates(self, task):
        indexes_to_update = []

        for date_field, index in TASK_DATE_FIELDS:
            value = getattr(task, date_field)
            if value and isinstance(value, datetime):
                setattr(task, date_field, value.date())
                if index:
                    indexes_to_update.append(index)

        if indexes_to_update:
            task.reindexObject(idxs=indexes_to_update)

    def fix_document_dates(self, document):
        indexes_to_update = []

        for date_field, index in DOCUMENT_DATE_FIELDS:
            value = getattr(document, date_field)
            if value and isinstance(value, datetime):
                setattr(document, date_field, value.date())
                if index:
                    indexes_to_update.append(index)

        if indexes_to_update:
            document.reindexObject(idxs=indexes_to_update)
