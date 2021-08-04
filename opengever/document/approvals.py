from datetime import datetime
from opengever.base.oguid import Oguid
from opengever.document.behaviors import IBaseDocument
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
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

    def add(self, approved, approver, task_oguid, version_id):
        """Add a new approval to the storage.
        """
        data = PersistentMapping({
            'approved': approved,
            'approver': approver,
            'task_oguid': task_oguid,
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

        self.storage.add(approved, approver,
                         Oguid.for_object(task), version_id)

    def get(self):
        return self.storage.list()
