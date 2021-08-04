from collections import defaultdict
from datetime import datetime
from opengever.document.behaviors import IBaseDocument
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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
