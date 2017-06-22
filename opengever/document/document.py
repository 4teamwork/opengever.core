from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.Permissions import webdav_unlock_items
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from five import grok
from ftw.mail.interfaces import IEmailAddress
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.interfaces import IRedirector
from opengever.document import _
from opengever.document.base import BaseDocumentMixin
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.officeconnector.helpers import create_oc_url
from opengever.task.task import ITask
from plone import api
from plone.autoform import directives as form_directives
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile import field
from plone.namedfile.file import NamedBlobFile
from z3c.form import validator
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
import logging
import os.path


# Note: the changeNote field from the IVersionable behavior is being dropped
# and moved in change_note.py - we do this in a separate module to avoid
# setting the tagged values too early (document.py gets imported in many
# places, to get the IDocumentSchema for example)


LOG = logging.getLogger('opengever.document')
MAIL_EXTENSIONS = ['.eml', '.msg']


class IDocumentSchema(form.Schema):
    """Document Schema Interface."""

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'title',
            u'file',
            ],
        )

    dexteritytextindexer.searchable('title')
    form_directives.order_before(title='IDocumentMetadata.description')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    form.primary('file')
    form_directives.order_after(file='IDocumentMetadata.document_author')
    file = field.NamedBlobFile(
        title=_(u'label_file', default='File'),
        description=_(u'help_file', default=''),
        required=False,
        )

    @invariant
    def title_or_file_required(data):
        if not data.title and not data.file:
            raise Invalid(_(u'error_title_or_file_required',
                            default=u'Either the title or the file is '
                            'required.'))


class UploadValidator(validator.SimpleFieldValidator):
    """Validate document uploads."""

    def validate(self, value):
        """An mail upload as og.document should't be possible,
        it should be added as Mail object (see opengever.mail).
        """
        if value and value.filename:
            basename, extension = os.path.splitext(value.filename)
            if extension.lower() in MAIL_EXTENSIONS:
                if IDossierMarker.providedBy(self.context):
                    mail_address = IEmailAddress(
                        self.request).get_email_for_object(self.context)
                else:
                    parent = aq_parent(aq_inner(self.context))
                    mail_address = IEmailAddress(
                        self.request).get_email_for_object(parent)

                raise Invalid(_(
                    u'error_mail_upload',
                    default=u"It's not possible to add E-mails here, please '\
                    'send it to ${mailaddress} or drag it to the dossier '\
                    ' (Dragn'n'Drop).",
                    mapping={'mailaddress': mail_address}
                    ))

            return


validator.WidgetValidatorDiscriminators(
    UploadValidator,
    field=IDocumentSchema['file'],
    )

grok.global_adapter(UploadValidator)


class Document(Item, BaseDocumentMixin):
    """Documents, the main data store of GEVER."""

    security = ClassSecurityInfo()

    implements(ITabbedviewUploadable)

    # document state's
    removed_state = 'document-state-removed'
    active_state = 'document-state-draft'
    shadow_state = 'document-state-shadow'

    remove_transition = 'document-transition-remove'
    restore_transition = 'document-transition-restore'
    initialize_transition = 'document-transition-initialize'

    # disable file preview creation when modifying or creating document
    buildPreview = False

    def __contains__(self, key):
        """Used because of a the following contains check in
        collective.quickupload:
        https://github.com/collective/collective.quickupload/blob/1.8.2/collective/quickupload/browser/quick_upload.py#L679
        """
        return False

    def related_items(self):
        relations = IRelatedDocuments(self).relatedItems
        if relations:
            return [rel.to_object for rel in relations]
        return []

    def getIcon(self, relative_to_portal=1):
        return self.get_mimetype_icon(relative_to_portal)

    def icon(self):
        """For ZMI."""
        return self.getIcon()

    def as_shadow_document(self):
        """Force a document into the shadow state.

        The shadow-state is an alternative initial state for documents created
        by the officeatwork integration.

        """
        wftool = api.portal.get_tool('portal_workflow')
        chain = wftool.getChainFor(self)
        workflow_id = chain[0]
        wftool.setStatusOf(workflow_id, self, {
            'review_state': self.shadow_state,
            'action': '',
            'actor': ''})
        workflow = wftool.getWorkflowById(workflow_id)
        workflow.updateRoleMappingsFor(self)
        return self

    def checked_out_by(self):
        manager = getMultiAdapter((self, self.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.get_checked_out_by()

    def is_checkout_and_edit_available(self):
        manager = queryMultiAdapter(
            (self, getRequest()), ICheckinCheckoutManager)

        if manager.get_checked_out_by():
            if manager.get_checked_out_by() == \
                    getSecurityManager().getUser().getId():
                return True
            else:
                return False

        return manager.is_checkout_allowed()

    def is_shadow_document(self):
        return api.content.get_state(self) == self.shadow_state

    def is_checked_out(self):
        return self.checked_out_by() is not None

    def is_movable(self):
        return not self.is_inside_a_task() and not self.is_inside_a_proposal()

    def is_inside_a_task(self):
        parent = aq_parent(aq_inner(self))
        return ITask.providedBy(parent)

    def is_inside_a_proposal(self):
        parent = aq_parent(aq_inner(self))
        return IProposal.providedBy(parent)

    def is_submitted_document(self):
        parent = aq_parent(aq_inner(self))
        return ISubmittedProposal.providedBy(parent)

    def can_be_submitted_as_additional_document(self):
        parent = aq_parent(aq_inner(self))
        return IDossierMarker.providedBy(parent)

    def get_current_version(self):
        """Return the current document history version."""
        repository = api.portal.get_tool("portal_repository")
        assert repository.isVersionable(self), \
            'Document is not versionable'
        history = repository.getHistoryMetadata(self)
        current_version = history.getLength(countPurged=False) - 1
        assert history.retrieve(current_version), \
            'missing history entry for verion {}'.format(current_version)
        return current_version

    def update_file(self, filename, content_type, data):
        self.file = NamedBlobFile(
            data=data,
            filename=filename,
            contentType=content_type)

    def has_file(self):
        return self.file is not None

    def get_file(self):
        return self.file

    def get_filename(self):
        if self.has_file():
            return self.file.filename
        return None

    security.declareProtected(webdav_unlock_items, 'UNLOCK')

    def UNLOCK(self, REQUEST, RESPONSE):
        """Leave shadow state if a shadow-document is unlocked.

        If we are in shadow state when unlocking the document it was created
        by officeatwork. In that case leave the shadow-state.

        """
        response = super(Document, self).UNLOCK(REQUEST, RESPONSE)

        if self.is_shadow_document():
            api.content.transition(
                self, transition='document-transition-initialize')

        return response

    def setup_external_edit_redirect(self, request):
        redirector = IRedirector(request)
        if is_officeconnector_checkout_feature_enabled():
            redirector.redirect(create_oc_url(
                request,
                self,
                dict(action='checkout'),
            ))
        else:
            redirector.redirect(
                '%s/external_edit' % self.absolute_url(),
                target='_self',
                timeout=1000)
