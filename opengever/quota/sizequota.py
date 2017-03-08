from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from opengever.quota.interfaces import IQuotaSubject
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface


def size_quotas_in_chain_of(context):
    """Generator with size quota adapter instances for each object in the
    acquisition chain which has a quota.
    """
    for parent in aq_chain(context):
        size_quota = ISizeQuota(parent, None)
        if size_quota:
            yield size_quota


class ISizeQuota(Interface):
    """Behavior for enabling a size quota for a container.
    """


class IContainerWithSizeQuota(Interface):
    """Marker interface for containers having a quota.
    """


class SizeQuota(object):
    """Size quota behavior adapter.
    """

    def __init__(self, context):
        self.context = context

    def get_usage(self):
        """Returns the current quota usage in bytes.
        """
        return sum((self.get_usage_map(for_writing=False) or {}).values())

    def update_object_usage(self, obj):
        """Update usage for an existing or a new object.
        """
        quota_subject = IQuotaSubject(obj, None)
        if not quota_subject:
            return

        self.get_usage_map(for_writing=True)[IUUID(obj)] = quota_subject.get_size()

    def remove_object_usage(self, obj):
        """Remove usage for a object which will be deleted or moved.
        """
        self.get_usage_map(for_writing=True).pop(IUUID(obj), 0)

    def get_usage_map(self, for_writing):
        """The usage map is a btree containing the size in bytes for each
        quota subject identified by UUID.
        """
        key = 'opengever.quota:size-usage'
        annotations = IAnnotations(self.context)
        if key not in annotations:
            if not for_writing:
                return None

            annotations[key] = OOBTree()

        return annotations[key]
