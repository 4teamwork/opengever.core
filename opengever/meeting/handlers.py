from five import grok
from OFS.interfaces import IObjectWillBeRemovedEvent
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectCheckedInEvent
from opengever.document.interfaces import IObjectRevertedToVersion
from opengever.meeting.command import UpdateExcerptInDossierCommand
from opengever.meeting.model import GeneratedExcerpt
from opengever.meeting.model import Proposal
from opengever.meeting.model import SubmittedDocument
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


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


@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def on_document_modified(context, event):
    _sync_excerpt(context)


@grok.subscribe(IDocumentSchema, IObjectCheckedInEvent)
def on_documed_checked_in(context, event):
    _sync_excerpt(context)


@grok.subscribe(IDocumentSchema, IObjectRevertedToVersion)
def on_document_reverted_to_version(context, event):
    _sync_excerpt(context)


def _sync_excerpt(document):
    if document.is_checked_out():
        return

    proposal = Proposal.query.join(
        GeneratedExcerpt, Proposal.submitted_excerpt_document).filter(
        GeneratedExcerpt.oguid == Oguid.for_object(document)).first()
    if not proposal:
        return

    UpdateExcerptInDossierCommand(proposal).execute()
