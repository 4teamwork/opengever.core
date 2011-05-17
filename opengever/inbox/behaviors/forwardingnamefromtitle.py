"""Contains a Behavior that gets the Forwardingname from Title"""
from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implements


class IForwardingNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class ForwardingNameFromTitle(object):
    """Speical name from title behavior for letting the normalizing name
    chooser choose the ID like want it to be.
    The id of a forwarding should be in the format: "forwarding-{sequence number}"
    """

    implements(IForwardingNameFromTitle)

    format = u'forwarding-%i'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        """Writes a property wich safes the id"""
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number
