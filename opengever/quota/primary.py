from opengever.quota.interfaces import IQuotaSubject
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IPrimaryBlobFieldQuota(Interface):
    """Behavior for counting the size of the primary field blob
    as usage.
    """


@implementer(IQuotaSubject)
@adapter(IPrimaryBlobFieldQuota)
class PrimaryFieldQuotaSubject(object):

    def __init__(self, context):
        self.context = context

    def get_size(self):
        """Return the current size of the context in bytes.
        """
        primary_field_info = IPrimaryFieldInfo(self.context, None)
        if not primary_field_info or not primary_field_info.value:
            return 0
        return primary_field_info.value.size
