from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.base.adapters import DefaultMovabilityChecker
from opengever.tasktemplates import _
from opengever.tasktemplates import is_tasktemplatefolder_nesting_allowed
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from zope.component import adapter


@adapter(ITaskTemplateFolderSchema)
class TaskTemplateFolderMovabiliyChecker(DefaultMovabilityChecker):

    def validate_movement(self, target):
        super(TaskTemplateFolderMovabiliyChecker, self).validate_movement(target)
        if not ITaskTemplateFolderSchema.providedBy(target):
            return

        if not is_tasktemplatefolder_nesting_allowed():
            raise NotReportedForbidden(
                _(u"msg_tasktemplatefolder_nesting_not_allowed",
                  u"It's not allowed to move tasktemplatefolders into tasktemplatefolders."))
