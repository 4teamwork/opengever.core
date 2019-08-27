from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.browser.paste import ICopyPasteRequestLayer
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.portlets import block_context_portlet_inheritance
from opengever.base.security import elevated_privileges
from opengever.meeting.activity.watchers import add_watcher_on_proposal_created
from opengever.meeting.command import UpdateExcerptInDossierCommand
from opengever.meeting.interfaces import IHistory
from opengever.meeting.model import GeneratedExcerpt
from opengever.meeting.model import Proposal
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.model.excerpt import Excerpt
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.proposalsqlsyncer import ProposalSqlSyncer
from opengever.meeting.proposalsqlsyncer import SubmittedProposalSqlSyncer
from opengever.meeting.sablontemplate import sablon_template_is_valid
from opengever.setup.interfaces import IDuringSetup
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds
import os


def document_deleted(context, event):
    """Fired when a document or a mail is deleted.

    This happens while rejecting proposals. The entry that tracks the submitted
    documents must also be removed to avoid issues when re-submitting.

    this event is also fired when deleting a plone site. Unfortunately
    no deletion-order seems to be guaranteed, so it might happen that the
    IntId utility is removed before removing content.
    """
    try:
        getUtility(IIntIds)
    except ComponentLookupError:
        return

    session = create_session()
    for doc in SubmittedDocument.query.by_document(context).all():
        session.delete(doc)


def excerpt_delete(context, event):
    # if it is an excerpt document from an agendaitem with a proposal,
    # remove the excerpt from the submitted proposal.
    for relation in getUtility(ICatalog).findRelations({
            'to_id': getUtility(IIntIds).getId(aq_inner(context)),
            'from_attribute': 'excerpts'}):
        # We expect that there are 0 or 1 relation, because this document
        # cannot be the excerpt of multiple proposals.
        submitted_proposal = relation.from_object
        assert(ISubmittedProposal.providedBy(submitted_proposal))
        submitted_proposal.remove_excerpt(context)
        return

    # if it is an excerpt document from an agendaitem without a proposal
    # remove it from the SQL database.
    Excerpt.query.by_oguid(Oguid.for_object(context)).delete()


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


def delete_copied_proposal(copied_proposal, event):
    """Prevent that proposals are copied.

    This deletes the proposal from the copied subtree (a ZEXP) before the
    subtree gets inserted into the destination location.

    Suppress deletion events in order to avoid attempts to uncatalog
    an object that
    1) hasn't even been cataloged yet
    2) doesn't have a proper AQ chain because it's parts of a subtree
       that only exists as a temporary ZEXP that hasn't been attached to
       a container yet
    """
    with elevated_privileges():
        container = aq_parent(copied_proposal)
        container._delObject(copied_proposal.id, suppress_events=True)


def proposal_moved(obj, event):
    # Skip automatically renamed objects during copy & paste process.
    if ICopyPasteRequestLayer.providedBy(getRequest()):
        return

    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    ProposalSqlSyncer(obj, event).sync()


def proposal_added(obj, event):
    add_watcher_on_proposal_created(obj)
    IHistory(obj).append_record(u'created')
    if obj.predecessor_proposal is not None:
        predecessor = obj.predecessor_proposal.to_object
        IHistory(predecessor).append_record(
            u'successor_created',
            successor_oguid=Oguid.for_object(obj).id)

    ProposalSqlSyncer(obj, event).sync()


def proposal_modified(obj, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    ProposalSqlSyncer(obj, event).sync()


def submitted_proposal_modified(obj, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    SubmittedProposalSqlSyncer(obj, event).sync()


def configure_committee_container_portlets(container, event):
    """Do not acquire portlets.
    """
    block_context_portlet_inheritance(container)


def validate_template_file(obj, event):
    # skip validation during setup of development system. This allows to setup
    # in development mode without the need of a working sablon installation.
    if IDuringSetup.providedBy(getRequest()) and os.environ.get('IS_DEVELOPMENT_MODE', False):
        return
    if obj.file is not None:
        IAnnotations(obj)[
            'opengever.meeting.sablon_template_is_valid'
        ] = sablon_template_is_valid(obj.file)
