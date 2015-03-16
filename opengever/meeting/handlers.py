from five import grok
from OFS.interfaces import IObjectWillBeRemovedEvent
from opengever.base.model import create_session
from opengever.document.document import IDocumentSchema
from opengever.meeting.model import SubmittedDocument
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.intid.interfaces import IIntIds


@grok.subscribe(IDocumentSchema, IObjectWillBeRemovedEvent)
def document_deleted(context, event):
    # this event is also fired when deleting a plone site. Unfortunately
    # no deletion-order seems to be guaranteed, so it might happen that the
    # IntId utility is removed before removing content.
    try:
        getUtility(IIntIds)
    except ComponentLookupError:
        return

    session = create_session()
    for doc in SubmittedDocument.query.by_document(context).all():
        session.delete(doc)
