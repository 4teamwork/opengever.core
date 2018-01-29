from opengever.base.browser.paste import ICopyPasteRequestLayer
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.portlets import block_context_portlet_inheritance
from opengever.base.security import elevated_privileges
from opengever.base.sqlsyncer import SqlSyncer
from opengever.meeting.command import UpdateExcerptInDossierCommand
from opengever.meeting.model import GeneratedExcerpt
from opengever.meeting.model import Proposal
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.sablontemplate import ISablonTemplate
from opengever.meeting.sablontemplate import sablon_template_is_valid
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds


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


def on_document_modified(context, event):
    _sync_excerpt(context)


def on_documed_checked_in(context, event):
    _sync_excerpt(context)


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


def delete_copied_proposal(obj, event):
    """Prevent that proposals are copied.

    Turns out the easiest way to accomplish this is to delete the proposal
    after it has been copied.
    """
    with elevated_privileges():
        api.content.delete(obj)


class ProposalSqlSyncer(SqlSyncer):

    def sync_with_sql(self):
        self.obj.sync_model()


def sync_moved_proposal(obj, event):
    # Skip automatically renamed objects during copy & paste process.
    if ICopyPasteRequestLayer.providedBy(getRequest()):
        return

    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    ProposalSqlSyncer(obj, event).sync()


def sync_proposal(obj, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    ProposalSqlSyncer(obj, event).sync()


def configure_committee_container_portlets(container, event):
    """Do not acquire portlets.
    """
    block_context_portlet_inheritance(container)


def validate_template_file(obj, event):
    if obj.file is not None:
        IAnnotations(obj)[
            'opengever.meeting.sablon_template_is_valid'
        ] = sablon_template_is_valid(obj.file)
