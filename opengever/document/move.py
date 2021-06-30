from OFS.CopySupport import ResourceLockedError
from opengever.base.adapters import DefaultMovabilityChecker
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
        if self.context.is_inside_a_task():
            raise Forbidden(u'Documents inside a task cannot be moved.')
        if self.context.is_inside_a_proposal():
            raise Forbidden(u'Documents inside a proposal cannot be moved.')
        if self.context.is_inside_a_closed_dossier():
            raise Forbidden(u'Documents inside a closed dossier cannot be moved.')
        if ILockable(self.context).locked():
            raise ResourceLockedError(u'Locked documents cannot be moved.')

        if is_within_repository(self.context):
            if is_within_templates(target):
                raise Forbidden(
                    u'Documents within the repository cannot be moved to the templates.')
            if is_within_private_root(target):
                raise Forbidden(
                    u'Documents within the repository cannot be moved to the private repository.')
            return

        if is_within_inbox(self.context):
            if is_within_templates(target):
                raise Forbidden(
                    u'Documents within the inbox cannot be moved to the templates.')
            if is_within_private_root(target):
                raise Forbidden(
                    u'Documents within the inbox cannot be moved to the private repository.')
