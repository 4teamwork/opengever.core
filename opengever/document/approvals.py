from datetime import datetime
from opengever.document.behaviors import IBaseDocument
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IApprovalList(Interface):
    """Interface to manage document approvals
    """


class ApprovalStorage(object):

    ANNOTATIONS_KEY = 'opengever.document.approvals'

    def __init__(self, context):
        self.context = context
        self._initialize_storage()

    def add(self, approved, approver, task_uid, version_id):
        """Add a new approval to the storage.
        """
        data = PersistentMapping({
            'approved': approved,
            'approver': approver,
            'task_uid': task_uid,
            'version_id': version_id})

        self._storage.append(data)

    def list(self):
        return list(self._storage)

    def _initialize_storage(self):
        ann = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in ann:
            ann[self.ANNOTATIONS_KEY] = PersistentList()

        self._storage = ann[self.ANNOTATIONS_KEY]


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
        return self.storage.list()

    def get_grouped_by_version_id(self):
        data = {}
        for approval in self.storage.list():
            version_id = approval.get('version_id')
            if approval.get('version_id') in data:
                data[version_id].append(approval)
            else:
                data[version_id] = [approval, ]

        return data
