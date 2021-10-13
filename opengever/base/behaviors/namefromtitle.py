from Acquisition import aq_base
from plone.app.content.interfaces import INameFromTitle
from zope.interface import implements


class IDefaultNameFromTitle(INameFromTitle):
    """Choose IDs for a disposition in the following format:
    "disposition-{sequence number}"
    """


class DefaultNameFromTitle(object):
    """Default name from title behavior setting the title to the portal_type
    """

    implements(IDefaultNameFromTitle)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return getattr(aq_base(self.context), 'portal_type', None)
