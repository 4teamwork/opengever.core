from zope.component.interfaces import ObjectEvent
from zope.interface import implements
from opengever.mail.interfaces import IDocumentSent
from zope.intid.interfaces import IIntIds
from zope.component import getUtility


class DocumentSent(ObjectEvent):
    """Local Roles has been modified"""

    implements(IDocumentSent)

    def __init__(self, object, sender, receiver, subject, message, attachments):
        """adf"""
        self.object = object
        self.sender = sender
        self.receiver = receiver.encode('utf-8')
        self.subject = subject.encode('utf-8')
        self.message = message.encode('utf-8')
        id_util = getUtility(IIntIds)
        intids = []
        for attachment in attachments:
            intids.append(id_util.queryId(attachment))
        self.intids = intids