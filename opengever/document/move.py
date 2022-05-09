from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.api.not_reported_exceptions import ResourceLockedError as NotReportedResourceLockedError
from opengever.base.adapters import DefaultMovabilityChecker
from opengever.document import _
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.templatefolder.utils import is_within_templates
from opengever.inbox.utils import is_within_inbox
from opengever.private.utils import is_within_private_root
from opengever.repository.utils import is_within_repository
from plone.locking.interfaces import ILockable
from zExceptions import Forbidden
from zope.component import adapter


@adapter(IBaseDocument)
class DocumentMovabiliyChecker(DefaultMovabilityChecker):

    def validate_movement(self, target):
        super(DocumentMovabiliyChecker, self).validate_movement(target)

        if self.context.is_inside_a_task():
            raise NotReportedForbidden(
                _(u'msg_doc_inside_task_cant_be_moved',
                  u'Documents inside a task cannot be moved.'))
        if self.context.is_inside_a_proposal():
            raise NotReportedForbidden(
                _(u'msg_doc_inside_proposal_cant_be_moved',
                  u'Documents inside a proposal cannot be moved.'))
        if self.context.is_inside_a_closed_dossier():
            raise NotReportedForbidden(
                _(u'msg_doc_inside_closed_dossier',
                  default=u'Documents inside a closed dossier cannot be moved.'))
        if ILockable(self.context).locked():
            raise NotReportedResourceLockedError(
                _('msg_locked_doc_cant_be_moved',
                  default=u'Locked documents cannot be moved.'))

        if is_within_repository(self.context):
            if is_within_templates(target):
                raise Forbidden(
                    _(u'msg_docs_cant_be_moved_from_repo_to_templates',
                      u'Documents within the repository cannot be moved to the templates.'))
            if is_within_private_root(target):
                raise Forbidden(
                    _(u'msg_docs_cant_be_moved_from_repo_to_private_repo',
                      u'Documents within the repository cannot be moved to the private repository.'))

        if is_within_inbox(self.context):
            if is_within_templates(target):
                raise Forbidden(
                    _(u'msg_docs_cant_be_moved_from_inbox_to_templates',
                      u'Documents within the inbox cannot be moved to the templates.'))
            if is_within_private_root(target):
                raise Forbidden(
                    _(u'msg_docs_cant_be_moved_from_inbox_to_private_repo',
                      u'Documents within the inbox cannot be moved to the private repository.'))
