from AccessControl.unauthorized import Unauthorized
from collections import defaultdict
from datetime import datetime
from opengever.document.behaviors import IBaseDocument
from opengever.document.versioner import Versioner
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


APPROVED_IN_CURRENT_VERSION = 'approved-in-current-version'
APPROVED_IN_OLDER_VERSION = 'approved-in-older-version'


class IApprovalList(Interface):
    """Interface to manage document approvals
    """


class Approval(object):

    def __init__(self, approved, approver, task_uid, version_id):
        self.approved = approved
        self.approver = approver
        self.task_uid = task_uid
        self.version_id = version_id

    def get_task_brain(self):
        return uuidToCatalogBrain(self.task_uid)


class ApprovalStorage(object):

    ANNOTATIONS_KEY = 'opengever.document.approvals'

    def __init__(self, context):
        self.context = context
        self._initialize_storage()

    def add(self, approved, approver, task_uid, version_id):
        """Add a new approval to the storage.
        """
        self._initialize_storage(create_if_missing=True)

        data = PersistentMapping({
            'approved': approved,
            'approver': approver,
            'task_uid': task_uid,
            'version_id': version_id})

        self._storage.append(data)

    def list(self):
        if not self._storage:
            return []

        return list(self._storage)

    def _initialize_storage(self, create_if_missing=False):
        ann = IAnnotations(self.context)
        if create_if_missing and self.ANNOTATIONS_KEY not in ann:
            ann[self.ANNOTATIONS_KEY] = PersistentList()

        self._storage = ann.get(self.ANNOTATIONS_KEY)

    def remove_all_except(self, except_version):
        """Removes all approval from the document except the ones for
        the given version."""

        if not self._storage:
            return

        except_approvals = PersistentList([
            approval for approval in self._storage
            if approval.get('version_id') == except_version])

        IAnnotations(self.context)[self.ANNOTATIONS_KEY] = except_approvals

    def remove_all(self):
        if self._storage:
            IAnnotations(self.context).pop(self.ANNOTATIONS_KEY)

    def reset_approvals_to_version(self, new_version_id):
        if not self._storage:
            return

        for item in self._storage:
            item['version_id'] = new_version_id


@implementer(IApprovalList)
@adapter(IBaseDocument)
class ApprovalList(object):

    def __init__(self, context):
        self.context = context
        self.storage = ApprovalStorage(context)

    def add(self, version_id, task, approver=None, approved=None):
        if not approver:
            approver = api.user.get_current().id

        if not approved:
            approved = datetime.now()

        self.storage.add(approved, approver, IUUID(task), version_id)
        self.context.reindexObject(idxs=['UID', 'approval_state'])

    def get(self):
        return list(self)

    def __iter__(self):
        for item in self.storage.list():
            yield Approval(**item)

    def get_grouped_by_version_id(self):
        data = defaultdict(list)
        for approval in self:
            version_id = approval.version_id
            data[version_id].append(approval)

        return data

    def cleanup_copied_approvals(self, current_version):
        """Remove approvals from previous versions and reset the version_id
        for the current version.
        """
        if current_version is None:
            return self.storage.remove_all()

        # Explicit reindexing of approval_state is not needed here.
        # The copied object will be indexed in its entirety on paste, during
        # ObjectAddedEvent, which is fired later than the ObjectCopiedEvent
        # this method is bound to.
        self.storage.remove_all_except(current_version)
        self.storage.reset_approvals_to_version(0)

    def get_approval_state(self):
        """Determine the approval stated based on existing approvals.

        - 'approved-in-current-version' if most recent version has been
          approved by at least one user.
        - 'approved-in-older-version' if a past version has been approved by
           at least one user (but the current one hasn't).
        - `None` otherwise (no approvals at all)
        """

        try:
            current_version_id = Versioner(self.context).get_current_version_id(
                missing_as_zero=True)
        except Unauthorized:
            # In some cases the current user is not allowed to access the history
            # metadata of the original object, in this case we remove all approvals
            return None

        approvals = self.get_grouped_by_version_id()

        current_version_approvals = approvals.get(current_version_id)
        old_version_approvals = {vid: a for vid, a in approvals.items()
                                 if vid < current_version_id}

        if current_version_approvals:
            return APPROVED_IN_CURRENT_VERSION
        elif old_version_approvals:
            return APPROVED_IN_OLDER_VERSION
        else:
            return None
