from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from ftw.mail.interfaces import IEmailAddress
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.interfaces import IRedirector
from opengever.base.model.favorite import Favorite
from opengever.base.utils import is_administrator
from opengever.docugate import is_docugate_feature_enabled
from opengever.docugate.interfaces import IDocumentFromDocugate
from opengever.document import _
from opengever.document.base import BaseDocumentMixin
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentSavedAsPDFMarker
from opengever.document.interfaces import IDocumentSettings
from opengever.document.versioner import Versioner
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting.proposal import ISubmittedProposal
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import is_client_ip_in_office_connector_disallowed_ip_ranges
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled
from opengever.officeconnector.mimetypes import get_editable_types
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.task.task import ITask
from opengever.virusscan.validator import validateUploadForFieldIfNecessary
from opengever.virusscan.validator import Z3CFormClamavValidator
from opengever.wopi.discovery import editable_extensions
from plone import api
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.autoform import directives as form
from plone.autoform.interfaces import OMITTED_KEY
from plone.dexterity.content import Item
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.namedfile import field
from plone.namedfile.file import NamedBlobFile
from plone.supermodel import model
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from z3c.form import validator
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implements
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.intid.interfaces import IIntIds
import logging
import os.path


DOCUMENT_FINALIZER_KEY = 'opengever.document.finalizer'
DOCUMENT_STATE_FINAL = 'document-state-final'
DOCUMENT_HAS_PENDING_CHANGES = '_document_has_pending_changes'

LOG = logging.getLogger('opengever.document')
MAIL_EXTENSIONS = ['.eml', '.msg', '.p7m']


# move the changeNote to the 'common' fieldset
IVersionable.setTaggedValue(FIELDSETS_KEY, [
    Fieldset('common', fields=[
             'changeNote',
             ])
])


# omit the changeNote from all forms because it's not possible to create a new
# version when editing document metadata
IVersionable.setTaggedValue(OMITTED_KEY, [
    (Interface, 'changeNote', 'true'),
    (IEditForm, 'changeNote', 'true'),
    (IAddForm, 'changeNote', 'true')])


def is_email_upload(filename):
    basename, extension = os.path.splitext(filename)
    return extension.lower() in MAIL_EXTENSIONS


class IDocumentSchema(model.Schema):
    """Document Schema Interface."""

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'title',
            u'file',
        ],
    )

    dexteritytextindexer.searchable('title')
    form.order_before(title='IDocumentMetadata.description')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    model.primary('file')
    form.order_after(file='IDocumentMetadata.document_author')
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

    @invariant
    def disallow_email_extensions(data):
        if data.file and is_email_upload(data.file.filename):
            raise Invalid(
                u"It is not possible to add E-mails as document, use "
                "portal_type ftw.mail.mail instead.")

    @invariant
    def scan_for_virus(data):
        if data.file:
            validateUploadForFieldIfNecessary(
                "file", data.file.filename, data.file.open(), getRequest())

    @invariant
    def disallow_blacklisted_mimetypes(data):
        if not data.file:
            return

        blacklisted_mimetypes = api.portal.get_registry_record(
            name='upload_mimetype_blacklist', interface=IDocumentSettings)

        if data.file.contentType in blacklisted_mimetypes:
            raise Invalid(
                _('error_blocked_mimetype_by_blacklist',
                  default="It is not allowed to upload this file format"))


class UploadValidator(Z3CFormClamavValidator):
    """Validate document uploads."""

    def validate(self, value):
        """An mail upload as og.document should't be possible,
        it should be added as Mail object (see opengever.mail).

        Only .docx files are accepted into proposal documents.

        Removing a file is not an option for proposal documents.
        """
        if self.request.form.get('form.widgets.file.action') == 'remove':
            if self.is_proposal_document_upload():
                raise Invalid(_(
                    u'error_proposal_no_document',
                    default=(u"It's not possible to have no file in proposal documents.")
                ))
        if not value:
            return

        if not value.filename:
            return

        # We duplicate this validation (there is also an form invariant) to
        # get a more detailed error message and directly shown by the field.
        if is_email_upload(value.filename):
            self.raise_invalid()

        if self.is_proposal_document_upload():
            if not os.path.splitext(value.filename)[1].lower() == '.docx':
                raise Invalid(_(
                    u'error_proposal_document_type',
                    default=(u"It's not possible to have non-.docx documents as proposal documents.")
                ))
        super(UploadValidator, self).validate(value)

    def is_proposal_document_upload(self):
        """The upload form context can be, for example, a Dossier."""
        return getattr(self.context, 'is_proposal_document', lambda: False)()

    def raise_invalid(self):
        if IDossierMarker.providedBy(self.context):
            mail_address = IEmailAddress(
                self.request).get_email_for_object(self.context)
        else:
            parent = aq_parent(aq_inner(self.context))
            mail_address = IEmailAddress(
                self.request).get_email_for_object(parent)

        # Remove widget value in order to disable that the widget renders
        # radio-buttons (nochange/remove/replace) once a file has been
        # uploaded.
        # This is a special case since we are an additional validator
        # for the file field that may block an otherwise valid file upload.
        # The widget does not expect this to happen though.
        if getattr(self.view.parentForm, '_nullify_file_on_error', False):
            self.widget.value = None

        raise Invalid(_(
            u'error_mail_upload',
            default=(u"It's not possible to add E-mails here, please "
                     u"send it to ${mailaddress} or drag it to the dossier "
                     u"(Dragn'n'Drop)."),
            mapping={'mailaddress': mail_address}
        ))


validator.WidgetValidatorDiscriminators(
    UploadValidator,
    field=IDocumentSchema['file'],
)


class Document(Item, BaseDocumentMixin):
    """Documents, the main data store of GEVER."""

    security = ClassSecurityInfo()

    implements(ITabbedviewUploadable)

    # document state's
    removed_state = 'document-state-removed'
    active_state = 'document-state-draft'
    shadow_state = 'document-state-shadow'
    final_state = 'document-state-final'

    remove_transition = 'document-transition-remove'
    restore_transition = 'document-transition-restore'
    initialize_transition = 'document-transition-initialize'
    finalize_transition = 'document-transition-finalize'
    reopen_transition = 'document-transition-reopen'

    workspace_workflow_id = 'opengever_workspace_document'

    # disable file preview creation when modifying or creating document
    buildPreview = False

    def __contains__(self, key):
        """Used because of a the following contains check in
        collective.quickupload:
        https://github.com/collective/collective.quickupload/blob/1.8.2/collective/quickupload/browser/quick_upload.py#L679
        """
        return False

    def sync_title_and_filename(self):
        """Syncs the document title and the filename.

        - If there is no title but a file, use the filename (without extension)
        as title.
        - If there is a title and a file, use the normalized title as filenames
        """
        if not self.file:
            return

        normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')

        # Correctly handle cases where both the filename and the title are
        # modified in the same request
        filename = getattr(self, "_v_filename", self.file.filename)
        title = getattr(self, "_v_title", self.title)

        basename, ext = os.path.splitext(filename)
        if not title:
            # use the filename without extension as title
            title = basename

        self.__dict__["title"] = title
        new_filename = normalizer.normalize(title, extension=ext)
        if self.get_filename() != new_filename:
            self.__dict__["file"].filename = new_filename
            Favorite.query.update_filename(self)

    @property
    def title(self):
        return self.__dict__.get('title')

    @title.setter
    def title(self, value):
        if self.title == value:
            return
        self.__dict__['title'] = value
        self._v_title = value
        self.sync_title_and_filename()

    @property
    def file(self):
        return self.__dict__.get('file')

    @file.setter
    def file(self, value):
        # For some reason this happens every time the edit form is saved, even
        # when the file was not modified
        if self.__dict__.get('file') == value:
            return

        if self.__dict__.get('file'):
            # Self is not aquisition wrapped, but we need an aquisition
            # wrapped object for checking/creating an initial version.
            document = api.content.get(UID=self.UID())

            # When retrieving a version, for example in the
            # opengever.bumblebee.download view, the document file attribute
            # is set by the CopyModifyMergeRepositoryTool._recursiveRetrieve.
            # Therefore we only create the initial version, if the document can
            # be aquisition wrapped
            if document:
                # Create an initial version before updating the document.
                Versioner(document).create_initial_version()

        self.__dict__['file'] = value
        self._v_filename = getattr(value, "filename", None)
        self.sync_title_and_filename()

    def related_items(self, include_forwardrefs=True, include_backrefs=False,
                      documents_only=False, tasks_only=False):
        _related_items = []

        if include_forwardrefs and not tasks_only:
            relations = IRelatedDocuments(self).relatedItems

            if relations:
                _related_items += [rel.to_object for rel in relations if not rel.isBroken()]

        if include_backrefs:
            catalog = getUtility(ICatalog)
            doc_id = getUtility(IIntIds).getId(aq_inner(self))
            relations = catalog.findRelations(
                {'to_id': doc_id, 'from_attribute': 'relatedItems'})

            if documents_only:
                relations = filter(
                    lambda rel: IBaseDocument.providedBy(rel.from_object),
                    relations)

            if tasks_only:
                relations = filter(
                    lambda rel: ITask.providedBy(rel.from_object),
                    relations)
            _related_items += [rel.from_object for rel in relations]

        return _related_items

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
        if workflow_id == self.workspace_workflow_id:
            # There is no shadow state for workspace documents.
            return self
        wftool.setStatusOf(workflow_id, self, {
            'review_state': self.shadow_state,
            'action': '',
            'actor': ''})
        workflow = wftool.getWorkflowById(workflow_id)
        workflow.updateRoleMappingsFor(self)
        self.reindexObject(idxs=['review_state'])
        self.reindexObjectSecurity()
        return self

    def leave_shadow_state(self):
        if self.is_shadow_document():
            api.content.transition(
                self, transition='document-transition-initialize')

    def is_finalize_allowed(self):
        return not self.is_checked_out() and \
            not self.is_referenced_by_pending_approval_task()

    def is_referenced_by_pending_approval_task(self):
        tasks = self.related_items(include_forwardrefs=False, include_backrefs=True, tasks_only=True)
        return any((task.is_pending() and task.is_approval_task() for task in tasks))

    def is_reopen_allowed(self):
        # reopen is not allowed if a pending task is referencing the document
        user = api.user.get_current()
        return ((is_administrator(user)
                 or user.getId() == self.finalizer)
                and not self.is_referenced_by_pending_approval_task())

    @property
    def finalizer(self):
        return IAnnotations(self).get(DOCUMENT_FINALIZER_KEY)

    @finalizer.setter
    def finalizer(self, value):
        IAnnotations(self)[DOCUMENT_FINALIZER_KEY] = value

    def checked_out_by(self):
        manager = getMultiAdapter((self, self.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.get_checked_out_by()

    def is_collaborative_checkout(self):
        manager = getMultiAdapter((self, self.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.is_collaborative_checkout()

    def get_collaborators(self):
        manager = getMultiAdapter((self, self.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.get_collaborators()

    def is_office_online_editable(self):
        filename = self.get_filename()
        if filename is None:
            return False
        name, ext = os.path.splitext(filename)
        if ext and ext[1:] in editable_extensions():
            return True
        return False

    def is_office_connector_editable(self):
        if self.file is None:
            return False

        editable_mimetypes = get_editable_types()
        return self.content_type().lower() in editable_mimetypes

    def is_checkout_and_edit_available(self):
        if is_client_ip_in_office_connector_disallowed_ip_ranges():
            return False

        manager = queryMultiAdapter(
            (self, getRequest()), ICheckinCheckoutManager)

        if manager.get_checked_out_by():
            if manager.is_collaborative_checkout():
                # Collaborative checkouts should never be mixed with regular
                # checkouts / OfficeConnector editing
                return False

            if manager.get_checked_out_by() == \
                    getSecurityManager().getUser().getId():
                return True
            else:
                return False

        return manager.is_checkout_allowed()

    def is_checkin_allowed(self):
        manager = queryMultiAdapter(
            (self, self.REQUEST), ICheckinCheckoutManager)
        return manager.is_checkin_allowed()

    def is_locked(self):
        manager = queryMultiAdapter(
            (self, self.REQUEST), ICheckinCheckoutManager)
        return manager.is_locked()

    def is_checkout_permitted(self):
        manager = queryMultiAdapter(
            (self, self.REQUEST), ICheckinCheckoutManager)
        return manager.is_checkout_permitted()

    def is_shadow_document(self):
        return api.content.get_state(self) == self.shadow_state

    def is_final_document(self):
        return api.content.get_state(self) == self.final_state

    def is_oneoffixx_creatable(self):
        return (is_oneoffixx_feature_enabled()
                and self.is_shadow_document()
                and not IDocumentSavedAsPDFMarker.providedBy(self))

    def is_docugate_creatable(self):
        return (is_docugate_feature_enabled()
                and self.is_shadow_document()
                and IDocumentFromDocugate.providedBy(self))

    def is_checked_out(self):
        return self.checked_out_by() is not None

    def is_submitted_document(self):
        parent = aq_parent(aq_inner(self))
        return ISubmittedProposal.providedBy(parent)

    def can_be_submitted_as_additional_document(self):
        parent = aq_parent(aq_inner(self))
        return IDossierMarker.providedBy(parent)

    def get_current_version_id(self, missing_as_zero=False):
        """Return the current document history version."""
        return Versioner(self).get_current_version_id(missing_as_zero)

    def update_file(self, data, content_type=None, filename=None,
                    create_version=False, comment=''):
        content_type = content_type or self.file.contentType
        filename = filename or self.file.filename

        self.file = NamedBlobFile(
            data=data,
            filename=filename,
            contentType=content_type)
        if create_version:
            Versioner(self).create_version(comment)
        self.setModificationDate()
        self.reindexObject()

    def has_file(self):
        return self.file is not None

    def get_file(self):
        return self.file

    def get_filename(self):
        if self.has_file():
            return self.file.filename
        return None

    def get_file_mtime(self):
        if self.has_file():
            return self.file._p_mtime
        return None

    @property
    def has_pending_changes(self):
        """True if the document has changes that haven't been checked-in yet.
        """
        return IAnnotations(self).get(DOCUMENT_HAS_PENDING_CHANGES, False)

    @has_pending_changes.setter
    def has_pending_changes(self, value):
        IAnnotations(self)[DOCUMENT_HAS_PENDING_CHANGES] = value

    def get_download_view_name(self):
        return 'download'

    def checkout_and_get_office_connector_url(self):
        """Checkout the document and return an office connector url.
        With the officeconnector checkout feature enabled, the checkout
        happens when the link is used.
        """
        if is_officeconnector_checkout_feature_enabled():
            return create_oc_url(self.REQUEST, self, {'action': 'checkout'})

        else:
            checkout_manager = getMultiAdapter((self, self.REQUEST),
                                               ICheckinCheckoutManager)
            if not checkout_manager.is_checked_out_by_current_user():
                checkout_manager.checkout()

            return '{}/external_edit'.format(self.absolute_url())

    def setup_external_edit_redirect(self, request, action='checkout'):
        redirector = IRedirector(request)
        if action == "checkout":
            if is_officeconnector_checkout_feature_enabled():
                redirector.redirect(create_oc_url(
                    request,
                    self,
                    dict(action=action),
                ))
            else:
                redirector.redirect(
                    '%s/external_edit' % self.absolute_url(),
                    target='_self',
                    timeout=1000)
        elif action == "oneoffixx" and is_oneoffixx_feature_enabled():
            redirector.redirect(create_oc_url(
                request,
                self,
                dict(action=action),
            ))
