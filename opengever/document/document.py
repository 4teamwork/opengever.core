from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.Permissions import webdav_unlock_items
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from ftw.mail.interfaces import IEmailAddress
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.base.interfaces import IRedirector
from opengever.document import _
from opengever.document.base import BaseDocumentMixin
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting.proposal import ISubmittedProposal
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.task.task import ITask
from plone import api
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.autoform import directives as form
from plone.autoform.interfaces import OMITTED_KEY
from plone.dexterity.content import Item
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


LOG = logging.getLogger('opengever.document')
MAIL_EXTENSIONS = ['.eml', '.msg']


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


class UploadValidator(validator.SimpleFieldValidator):
    """Validate document uploads."""

    def validate(self, value):
        """An mail upload as og.document should't be possible,
        it should be added as Mail object (see opengever.mail).

        Only .docx files are accepted into proposal documents.

        Removing a file is not an option for proposal documents.
        """
        if self.request.form.get('form.widgets.file.action') == 'remove':
            if self.is_proposal_upload():
                raise Invalid(_(
                    u'error_proposal_no_document',
                    default=(u"It's not possible to have no file in proposal documents.")
                    ))
        if not value:
            return

        if not value.filename:
            return

        if self.is_email_upload(value.filename):
            self.raise_invalid()

        if self.is_proposal_upload():
            if not os.path.splitext(value.filename)[1].lower() == '.docx':
                raise Invalid(_(
                    u'error_proposal_document_type',
                    default=(u"It's not possible to have non-.docx documents as proposal documents.")
                    ))

    def is_proposal_upload(self):
        """The upload form context can be, for example, a Dossier."""
        return getattr(self.context, 'is_inside_a_proposal', lambda: False)()

    def is_email_upload(self, filename):
        basename, extension = os.path.splitext(filename)
        return extension.lower() in MAIL_EXTENSIONS

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
            "send it to ${mailaddress} or drag it to the dossier "
            "(Dragn'n'Drop)."),
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

    @property
    def file(self):
        return self.__dict__.get('file')

    @file.setter
    def file(self, value):
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

    def related_items(self, bidirectional=False, documents_only=False):
        _related_items = []

        relations = IRelatedDocuments(self).relatedItems

        if relations:
            _related_items += [rel.to_object for rel in relations]

        if bidirectional:
            catalog = getUtility(ICatalog)
            doc_id = getUtility(IIntIds).getId(aq_inner(self))
            relations = catalog.findRelations(
                {'to_id': doc_id, 'from_attribute': 'relatedItems'})

            if documents_only:
                relations = filter(
                    lambda rel: IBaseDocument.providedBy(rel.from_object),
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
        wftool.setStatusOf(workflow_id, self, {
            'review_state': self.shadow_state,
            'action': '',
            'actor': ''})
        workflow = wftool.getWorkflowById(workflow_id)
        workflow.updateRoleMappingsFor(self)
        self.reindexObjectSecurity()
        return self

    def checked_out_by(self):
        manager = getMultiAdapter((self, self.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.get_checked_out_by()

    def is_office_connector_editable(self):
        if self.file is None:
            return False
        editable_mimetypes = [record.lower() for record in api.portal.get_registry_record(
            'opengever.officeconnector.interfaces.IOfficeConnectorSettings.officeconnector_editable_types')]
        return self.content_type().lower() in editable_mimetypes

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

    def get_download_view_name(self):
        return 'download'

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
