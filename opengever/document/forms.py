from AccessControl import getSecurityManager
from opengever.base.command import CreateDocumentCommand
from opengever.base.source import RepositoryPathSourceBinder
from opengever.document import _
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_SOURCE_UUID_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_SOURCE_VERSION_KEY
from opengever.document.document import IDocumentSchema
from opengever.document.versioner import Versioner
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentSavedAsPDFMarker
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from opengever.document.interfaces import NO_DOWNLOAD_INPUT_MODE
from opengever.dossier.base import DOSSIER_STATES_OPEN
from plone import api
from plone.autoform import directives
from plone.dexterity.browser import add
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.utils import iterSchemataForType
from plone.uuid.interfaces import IUUID
from plone.z3cform import layout
from zope.annotation import IAnnotations
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import validator
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import Interface, Invalid
from zope.intid.interfaces import IIntIds
from zope.schema import getFieldsInOrder
from zope.schema import Int
import z3c.form


class DocumentAddForm(add.DefaultAddForm):
    """Provide a file upload form for Documents.

    Nullifies uploaded file on a validation error.
    """

    # hackishly tell validator to nullify uploaded file on validation
    # errors for this add form.
    _nullify_file_on_error = True


class DocumentAddView(add.DefaultAddView):
    """Provide a registerable view for the Document file upload form."""

    form = DocumentAddForm


class DocumentEditForm(DefaultEditForm):
    """Custom edit form for documents, which displays some
    different and customized edit modes.
    """

    def updateWidgets(self):
        """Using document specific formwidget.namedfile modes.
        """
        super(DocumentEditForm, self).updateWidgets()

        # get the checkin checkout manager
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            return

        filefields = [
            g.fields.get('file')
            for g in self.groups
            if 'file' in g.fields
            ]

        if filefields > 0:
            file_field = filefields[0]

            current_user_id = getSecurityManager().getUser().getId()
            if self.context.digitally_available:
                if manager.get_checked_out_by() == current_user_id:
                    file_field.mode = NO_DOWNLOAD_INPUT_MODE
                else:
                    file_field.mode = NO_DOWNLOAD_DISPLAY_MODE
            else:
                file_field.mode = NO_DOWNLOAD_INPUT_MODE


DocumentEditView = layout.wrap_form(DocumentEditForm)


class IDocumentFileUploadForm(IDocumentSchema):
    """Schema for the file upload form."""

    directives.omitted('title')


class DocumentFileUploadForm(DefaultEditForm):
    """A form for just uploading the file of a document without any metadata
    fields. Used by Office Connector.
    """

    schema = IDocumentFileUploadForm
    additionalSchemata = ()
    render_form = True

    @button.buttonAndHandler(u'oc-file-upload', name='upload')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            self.request.response.setStatus(400)
            return

        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager.is_checked_out_by_current_user():
            self.request.response.setStatus(412)
            return

        self.applyChanges(data)
        self.request.response.setStatus(204)
        notify(EditFinishedEvent(self.context))
        self.render_form = False

    def render(self):
        if self.render_form:
            return super(DocumentFileUploadForm, self).render()
        self.request.response.setHeader('content-type', 'text/plain')
        return None


class ISaveAsPdfSchema(Interface):

    destination_folder = RelationChoice(
        title=_('label_destination', default="Destination"),
        description=_('help_destination',
                      default="Live Search: search for the dossier"),
        source=RepositoryPathSourceBinder(
            object_provides=[
                'opengever.dossier.behaviors.dossier.IDossierMarker',
                ],
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                ],
                'review_state': DOSSIER_STATES_OPEN + [
                    'repositoryfolder-state-active',
                    'repositoryroot-state-active']
                }
            ),
        required=True,
        )

    version_id = Int(
        title=_('version_id', default='Document Version'),
        required=False,
    )


class SavePDFUnderForm(form.Form):

    fields = field.Fields(ISaveAsPdfSchema)
    ignoreContext = True
    label = _('heading_save_as_pdf', default="Save as PDF")

    def update(self):
        version_id = self.request.get("version_id")

        if not self.check_version_is_convertable(version_id):
            msg = _(u'unconvertable_document',
                    default=u'This document cannot be converted to PDF.')
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        super(SavePDFUnderForm, self).update()
        self.widgets["version_id"].value = version_id

    def check_version_is_convertable(self, version_id):
        """ The object action is only available for documents that are convertable,
        but in the version tab, there is a link for each version and convertability
        is not checked. We therefore only check if it is convertable for requests
        with a version_id parameter.
        """
        if not version_id:
            return True
        document = Versioner(self.context).retrieve(version_id)
        return IBumblebeeServiceV3(self.request).is_convertable(document)

    def updateWidgets(self):
        super(SavePDFUnderForm, self).updateWidgets()
        self.widgets['version_id'].mode = HIDDEN_MODE

    @z3c.form.button.buttonAndHandler(_(u'button_submit',
                                        default=u'Save'))
    def handle_submit(self, action):
        data, errors = self.extractData()

        if len(errors) > 0:
            return

        self.destination = data['destination_folder']
        self.version_id = data.get("version_id")
        self.destination_document = self.create_destination_document()
        return self.request.RESPONSE.redirect(self.get_save_pdf_under_url())

    @z3c.form.button.buttonAndHandler(_(u'button_cancel',
                                        default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def get_save_pdf_under_url(self):
        save_pdf_under_url = '{}/demand_document_pdf'.format(self.destination_document.absolute_url())
        return save_pdf_under_url

    def create_destination_document(self):
        # get all the metadata that will be set on the created file.
        # We blacklist some fields that should not be copied
        fields_to_skip = set(("file",
                              "archival_file",
                              "archival_file_state",
                              "thumbnail",
                              "preview",
                              "digitally_available",
                              "changeNote",
                              "changed",
                              "relatedItems",))
        metadata = {}
        for schema in iterSchemataForType(self.context.portal_type):
            for name, schema_field in getFieldsInOrder(schema):
                if name in fields_to_skip:
                    continue
                field_instance = schema_field.bind(self.context)
                metadata[name] = field_instance.get(self.context)

        command = CreateDocumentCommand(self.destination, None, None, **metadata)
        destination_document = command.execute()

        # We make it in shadow state until its file is set by the callback view
        destination_document.as_shadow_document()
        # Add marker interface. This should be useful in the future for
        # cleanup jobs, retries if the PDF was not delivered and so on.
        alsoProvides(destination_document, IDocumentSavedAsPDFMarker)
        # Add annotations needed for the SavePDFDocumentUnder view.
        annotations = IAnnotations(destination_document)
        annotations[PDF_SAVE_SOURCE_UUID_KEY] = IUUID(self.context)
        annotations[PDF_SAVE_SOURCE_VERSION_KEY] = self.version_id

        # The missing_value attribute of a z3c-form field is used
        # as soon as an object has no default_value i.e. after creating
        # an object trough the command-line.
        #
        # Because the relatedItems field needs a list as a missing_value,
        # we will fall into the "mutable keyword argument"-python gotcha.
        # The relatedItems will be shared between the object-instances.
        #
        # Unfortunately the z3c-form field does not provide a
        # missing_value-factory (like the defaultFactory) which would be
        # necessary to fix this issue properly.
        #
        # As a workaround we make sure that the new document's relatedItems
        # is different object from the source document's.
        IRelatedDocuments(destination_document).relatedItems = list(
            IRelatedDocuments(destination_document).relatedItems)

        IRelatedDocuments(destination_document).relatedItems.append(
            RelationValue(getUtility(IIntIds).getId(self.context)))

        msg = _(u'Document ${document} was successfully created in ${destination}',
                mapping={"document": destination_document.title, "destination": self.destination.title})
        api.portal.show_message(msg, self.request, type='info')

        return destination_document


class SavePDFUnderFormView(layout.FormWrapper):
    """ View to save a document as PDF in another location
    """

    form = SavePDFUnderForm

    def render(self):
        return super(SavePDFUnderFormView, self).render()


class NotInContentTypes(Invalid):
    __doc__ = _(u"error_NotInContentTypes",
                default=u"User is not allowed to add a document there.")


class DestinationValidator(validator.SimpleFieldValidator):
    """Validator for destination-path.
    We check that the source-typ is allowed in the destination.
    We also check that the user has the required permissions to add
    content in the destination object.
    """

    def validate(self, value):
        super(DestinationValidator, self).validate(value)

        # Allowed contenttypes for destination-folder
        allowed_types = [t.getId() for t in value.allowedContentTypes()]

        if self.context.portal_type not in allowed_types:
            raise NotInContentTypes(
                _(u"error_NotInContentTypes",
                  default=u"User is not allowed to add a document there."))


validator.WidgetValidatorDiscriminators(
    DestinationValidator, field=ISaveAsPdfSchema['destination_folder'])
