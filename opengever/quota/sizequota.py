from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from opengever.quota import _
from opengever.quota.exceptions import ForbiddenByQuota
from opengever.quota.interfaces import HARD_LIMIT_EXCEEDED
from opengever.quota.interfaces import IObjectSize
from opengever.quota.interfaces import IQuotaSizeSettings
from opengever.quota.interfaces import SOFT_LIMIT_EXCEEDED
from opengever.quota.primary import IQuotaSubject
from plone import api
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
import logging


LOG = logging.getLogger('opengever.quota')


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

    def exceeded_limit(self):
        """Returns
        - ``HARD_LIMIT_EXCEEDED`` when the hard limit is exceeded,
        - ``SOFT_LIMIT_EXCEEDED`` when the soft limit is exceeded
        - else ``None``
        """
        usage = self.get_usage()
        settings = IQuotaSizeSettings(self.context)
        soft_limit = settings.get_soft_limit()
        hard_limit = settings.get_hard_limit()

        if hard_limit and usage > hard_limit:
            return HARD_LIMIT_EXCEEDED
        elif soft_limit and usage > soft_limit:
            return SOFT_LIMIT_EXCEEDED
        else:
            return None

    def update_object_usage(self, obj):
        """Update usage for an existing or a new object.
        """
        quota_subject = IObjectSize(obj, None)
        if not quota_subject:
            return

        usage_before = self.get_usage()
        self.get_usage_map(for_writing=True)[IUUID(obj)] = quota_subject.get_size()
        usage_after = self.get_usage()

        if self.exceeded_limit() == HARD_LIMIT_EXCEEDED \
           and usage_after > usage_before:
            if self.bypass_hardlimit():
                LOG.warning('Hard limit violation by admin.')
            else:
                message = _(u'Can not add this item'
                            u' because it exhausts the quota.')
                raise ForbiddenByQuota(message, container=self.context)

    def remove_object_usage(self, obj):
        """Remove usage for a object which will be deleted or moved.
        """
        self.get_usage_map(for_writing=True).pop(IUUID(obj), 0)

    def recalculate(self):
        """Clear and recalculate usage.
        """
        catalog = api.portal.get_tool('portal_catalog')
        portal = api.portal.get()

        for brain in catalog.unrestrictedSearchResults({
                'object_provides': IQuotaSubject.__identifier__}):
            obj = portal.unrestrictedTraverse(brain.getPath())
            self.update_object_usage(obj)

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

    def bypass_hardlimit(self):
        if api.user.is_anonymous():
            return False
        return 'Manager' in api.user.get_roles(obj=self.context)
