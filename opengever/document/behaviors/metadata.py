from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from datetime import date
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.vocabularies import KeywordSearchableAndAddableSourceBinder
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.mail.mail import IMail
from opengever.document import _
from opengever.document.interfaces import IDocumentSettings
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from z3c.form import validator
from z3c.form.browser import checkbox
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid


def document_date_default():
    """Set today's date as the default `document_date`"""
    return date.today()


def preserved_as_paper_default():
    """Set the client specific default for `preserved_as_paper`
    (configured in registry).
    """
    return api.portal.get_registry_record(
        'preserved_as_paper_default', interface=IDocumentSettings)


class IDocumentMetadata(model.Schema):
    """Schema behavior for common GEVER document metadata
    """

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'description',
            u'keywords',
            u'foreign_reference',
            u'document_date',
            u'receipt_date',
            u'delivery_date',
            u'document_type',
            u'document_author',
            u'digitally_available',
            u'preserved_as_paper',
            u'thumbnail',
            u'preview',
            ],
        )

    model.fieldset(
        u'archive_file',
        label=_(u'fieldset_archive_file', u'Archive file'),
        fields=[u'archival_file']
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        required=False,
        missing_value=u'',
        )

    form.widget('keywords', KeywordFieldWidget, new_terms_as_unicode=True, async=True)
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=ChoicePlus(
            source=KeywordSearchableAndAddableSourceBinder()
        ),
        required=False,
        missing_value=(),
        default=(),
    )

    foreign_reference = schema.TextLine(
        title=_(u'label_foreign_reference', default='Foreign Reference'),
        description=_('help_foreign_reference', default=''),
        required=False,
        )

    # workaround because ftw.datepicker wasn't working
    form.widget(document_date=DatePickerFieldWidget)
    document_date = schema.Date(
        title=_(u'label_document_date', default='Document Date'),
        description=_(u'help_document_date', default=''),
        required=False,
        defaultFactory=document_date_default,
        )

    # workaround because ftw.datepicker wasn't working
    form.widget(receipt_date=DatePickerFieldWidget)
    receipt_date = schema.Date(
        title=_(u'label_receipt_date', default='Date of receipt'),
        description=_(u'help_receipt_date', default=''),
        required=False,
        )

    # workaround because ftw.datepicker wasn't working
    form.widget(delivery_date=DatePickerFieldWidget)
    delivery_date = schema.Date(
        title=_(u'label_delivery_date', default='Date of delivery'),
        description=_(u'help_delivery_date', default=''),
        required=False,
        )

    document_type = schema.Choice(
        title=_(u'label_document_type', default='Document Type'),
        source=wrap_vocabulary(
            'opengever.document.document_types',
            visible_terms_from_registry='opengever.document.'
                                        'interfaces.IDocumentType.'
                                        'document_types'),
        required=False,
        )

    dexteritytextindexer.searchable('document_author')
    document_author = schema.TextLine(
        title=_(u'label_author', default='Author'),
        description=_(u'help_author',
                      default="Surname firstname or a userid"
                      "(would be automatically resolved to fullname)"),
        required=False,
        )

    form.mode(digitally_available='hidden')
    digitally_available = schema.Bool(
        title=_(u'label_digitally_available', default='Digital Available'),
        required=False,
        )

    form.widget(preserved_as_paper=checkbox.SingleCheckBoxFieldWidget)
    preserved_as_paper = schema.Bool(
        title=_(u'label_preserved_as_paper', default='Preserved as paper'),
        description=_(u'help_preserved_as_paper', default=''),
        required=False,
        defaultFactory=preserved_as_paper_default,
        )

    form.read_permission(archival_file='opengever.document.ModifyArchivalFile')
    form.write_permission(archival_file='opengever.document.ModifyArchivalFile')
    archival_file = NamedBlobFile(
        title=_(u'label_archival_file', default='Archival File'),
        description=_(u'help_archival_file', default=''),
        required=False,
    )

    form.omitted('archival_file_state')
    archival_file_state = schema.Int(
        title=_(u'label_archival_file_state', default='Archival file state'),
        required=False,
    )

    form.omitted('thumbnail')
    thumbnail = NamedBlobFile(
        title=_(u'label_thumbnail', default='Thumbnail'),
        required=False,
        )

    form.omitted('preview')
    preview = NamedBlobFile(
        title=_(u'label_preview', default='Preview'),
        description=_(u'help_preview', default=''),
        required=False,
        )


alsoProvides(IDocumentMetadata, IFormFieldProvider)


class FileOrPaperValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        """The document must either have a digital file or be preserved
        in paper form.

        XXX: This validator is a hack, since it validates field values across
        schemata using request.form instead of `value`.
        """
        # Bail if not called during a regular add form
        if self.request.form == {}:
            return

        # Mails are always available in digital form
        if IMail.providedBy(self.context):
            return

        form = self.view.parentForm
        if getattr(form, 'skip_validate_file_field', False):
            return

        if not any([self.has_file(),
                    self.is_preserved_as_paper(),
                    self.has_referenced_document()]):
            raise Invalid(
                _(u'error_file_and_preserved_as_paper',
                  default=u"You don't select a file and document is also not "
                          u"preserved in paper_form, please correct it."))

    def has_referenced_document(self):
        RELATED_DOCUMENTS_KEY = 'form.widgets.IRelatedDocuments.relatedItems'
        related_documents = self.request.form.get(RELATED_DOCUMENTS_KEY)
        return related_documents is not None and len(related_documents) > 0

    def is_preserved_as_paper(self):
        PAPER_KEY = 'form.widgets.IDocumentMetadata.preserved_as_paper'
        return self.request.form.get(PAPER_KEY) == [u'selected']

    def has_file(self):
        FILE_KEY = 'form.widgets.file'
        FILE_ACTION_KEY = '%s.action' % FILE_KEY
        file_added = bool(self.request.form.get(FILE_KEY))
        file_action = self.request.form.get(FILE_ACTION_KEY)
        if file_action == 'remove':
            return False

        return file_added or file_action


validator.WidgetValidatorDiscriminators(
    FileOrPaperValidator,
    field=IDocumentMetadata['preserved_as_paper'],
    )
