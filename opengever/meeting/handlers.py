from five import grok
from OFS.interfaces import IObjectWillBeRemovedEvent
from opengever.base.model import create_session
from opengever.document.document import IDocumentSchema
from opengever.meeting.model import SubmittedDocument


@grok.subscribe(IDocumentSchema, IObjectWillBeRemovedEvent)
def document_deleted(context, event):
    session = create_session()
    for doc in SubmittedDocument.query.by_document(context).all():
        session.delete(doc)
